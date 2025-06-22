# Standard library imports
import io
import os
from datetime import datetime
from typing import Optional, Any

# Third-party imports
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, Text, Boolean, DateTime
from sqlalchemy.orm import relationship
import docx

# Local imports
from config import config
from forms import LoginForm, CoupleForm, CeremonyTemplateForm
from services.gmail_service import GmailService

# Initialize Flask app
app = Flask(__name__)

# Load configuration
env = os.environ.get('FLASK_ENV', 'default')
app.config.from_object(config[env])

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    """User model for celebrants."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    name = Column(String(100), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    couples = relationship('Couple', backref='celebrant', lazy=True)
    templates = relationship('CeremonyTemplate', backref='celebrant', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Couple(db.Model):
    """Model for engaged couples."""
    __tablename__ = 'couples'
    
    id = Column(Integer, primary_key=True)
    celebrant_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    template_id = Column(Integer, ForeignKey('ceremony_templates.id'))
    
    # Partner 1 details
    partner1_name = Column(String(100), nullable=False)
    partner1_email = Column(String(120), nullable=False)
    partner1_phone = Column(String(20))
    
    # Partner 2 details
    partner2_name = Column(String(100), nullable=False)
    partner2_email = Column(String(120), nullable=False)
    partner2_phone = Column(String(20))
    
    # Ceremony details
    ceremony_date = Column(DateTime)
    ceremony_location = Column(String(200))
    ceremony_type = Column(String(50))
    
    # Status tracking
    status = Column(String(50), default='Inquiry')
    notes = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    template = relationship('CeremonyTemplate', backref='couples', foreign_keys=[template_id])

class CeremonyTemplate(db.Model):
    """Model for ceremony templates."""
    __tablename__ = 'ceremony_templates'
    
    id = Column(Integer, primary_key=True)
    celebrant_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    name = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    is_default = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.query.get(int(user_id))

# Routes
@app.route('/')
@login_required
def index():
    """Display the dashboard with upcoming ceremonies."""
    upcoming_couples = Couple.query.filter_by(celebrant_id=current_user.id)\
        .filter(Couple.status != 'Completed')\
        .filter(Couple.status != 'Cancelled')\
        .order_by(Couple.ceremony_date.asc())\
        .all()
    return render_template('index.html', couples=upcoming_couples)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid email or password')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    return redirect(url_for('login'))

# Couple Management Routes
@app.route('/couples')
@login_required
def couples_list():
    couples = Couple.query.filter_by(celebrant_id=current_user.id)\
        .order_by(Couple.ceremony_date.asc())\
        .all()
    return render_template('couples/list.html', couples=couples)

@app.route('/couples/new', methods=['GET', 'POST'])
@login_required
def couple_new():
    form = CoupleForm()
    if form.validate_on_submit():
        couple = Couple(  # type: ignore
            partner1_name=form.partner1_name.data,
            partner1_email=form.partner1_email.data,
            partner1_phone=form.partner1_phone.data,
            partner2_name=form.partner2_name.data,
            partner2_email=form.partner2_email.data,
            partner2_phone=form.partner2_phone.data,
            ceremony_date=form.ceremony_date.data,
            ceremony_location=form.ceremony_location.data,
            status=form.status.data,
            notes=form.notes.data,
            celebrant_id=current_user.id
        )
        db.session.add(couple)
        db.session.commit()
        flash('Couple added successfully!', 'success')
        return redirect(url_for('couples_list'))
    return render_template('couples/new.html', form=form)

@app.route('/couples/<int:id>')
@login_required
def couple_view(id: int):
    couple = Couple.query.filter_by(id=id, celebrant_id=current_user.id).first_or_404()
    return render_template('couples/view.html', couple=couple)

@app.route('/couples/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def couple_edit(id: int):
    couple = Couple.query.filter_by(id=id, celebrant_id=current_user.id).first_or_404()
    form = CoupleForm(obj=couple)
    
    if form.validate_on_submit():
        form.populate_obj(couple)  # type: ignore
        db.session.commit()
        flash('Couple updated successfully!', 'success')
        return redirect(url_for('couple_view', id=id))
    
    return render_template('couples/edit.html', couple=couple, form=form)

@app.route('/couples/<int:id>/delete', methods=['POST'])
@login_required
def couple_delete(id: int):
    couple = Couple.query.filter_by(id=id, celebrant_id=current_user.id).first_or_404()
    db.session.delete(couple)
    db.session.commit()
    flash('Couple deleted successfully!', 'success')
    return redirect(url_for('couples_list'))

# Ceremony Template Routes
@app.route('/templates')
@login_required
def templates_list():
    templates = CeremonyTemplate.query.filter_by(celebrant_id=current_user.id)\
        .order_by(CeremonyTemplate.name)\
        .all()
    return render_template('templates/list.html', templates=templates)

def extract_text_from_docx(file_stream: io.BytesIO) -> str:
    """Extract text content from a DOCX file."""
    doc = docx.Document(file_stream)
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return '\n\n'.join(full_text)

def handle_template_upload(form: CeremonyTemplateForm) -> Optional[str]:
    """Handle template file upload and return the content."""
    if not form.template_file.data:
        return None
        
    file = form.template_file.data
    content = None
    
    try:
        if file.filename.endswith('.docx'):
            # Handle DOCX files
            file_stream = io.BytesIO(file.read())
            content = extract_text_from_docx(file_stream)
        elif file.filename.endswith('.txt'):
            # Handle TXT files
            content = file.read().decode('utf-8')
        elif file.filename.endswith('.doc'):
            flash('Warning: DOC format is not fully supported. Please convert to DOCX for better results.', 'warning')
            # Basic text extraction (might not preserve formatting)
            content = file.read().decode('utf-8', errors='ignore')
            
        return content
    except Exception as e:
        flash(f'Error processing file: {str(e)}', 'error')
        return None

@app.route('/templates/new', methods=['GET', 'POST'])
@login_required
def template_new():
    form = CeremonyTemplateForm()
    if form.validate_on_submit():
        # Handle file upload if provided
        uploaded_content = handle_template_upload(form)
        
        template = CeremonyTemplate(
            name=form.name.data,
            content=uploaded_content or form.content.data,  # Use uploaded content if available
            is_default=form.is_default.data,
            celebrant_id=current_user.id
        )
        
        # If this is set as default, unset other defaults of the same type
        if template.is_default:
            CeremonyTemplate.query.filter_by(
                celebrant_id=current_user.id,
                is_default=True
            ).update({'is_default': False})
        
        db.session.add(template)
        db.session.commit()
        flash('Template created successfully!', 'success')
        return redirect(url_for('templates_list'))
        
    return render_template('templates/new.html', form=form)

@app.route('/templates/<int:id>')
@login_required
def template_view(id: int):
    template = CeremonyTemplate.query.filter_by(id=id, celebrant_id=current_user.id).first_or_404()
    return render_template('templates/view.html', template=template)

@app.route('/templates/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def template_edit(id: int):
    template = CeremonyTemplate.query.filter_by(id=id, celebrant_id=current_user.id).first_or_404()
    form = CeremonyTemplateForm(obj=template)
    
    if form.validate_on_submit():
        form.populate_obj(template)  # type: ignore
        db.session.commit()
        flash('Template updated successfully!', 'success')
        return redirect(url_for('template_view', id=id))
    
    return render_template('templates/edit.html', template=template, form=form)

@app.route('/templates/<int:id>/delete', methods=['POST'])
@login_required
def template_delete(id: int):
    template = CeremonyTemplate.query.filter_by(id=id, celebrant_id=current_user.id).first_or_404()
    db.session.delete(template)
    db.session.commit()
    flash('Template deleted successfully!', 'success')
    return redirect(url_for('templates_list'))

@app.route('/scan_emails', methods=['GET', 'POST'])
@login_required
def scan_emails():
    app.logger.info("Starting scan_emails route")
    credentials_exist = os.path.exists('credentials.json')
    token_exists = os.path.exists('token.pickle')
    scan_results = []
    
    app.logger.info(f"Credentials exist: {credentials_exist}")
    app.logger.info(f"Token exists: {token_exists}")
    
    if request.method == 'POST':
        try:
            app.logger.info("Creating Gmail service instance")
            gmail_service = GmailService()
            
            app.logger.info("Ensuring Gmail authentication")
            # This will raise an appropriate exception if authentication is needed
            gmail_service.ensure_authenticated()
            
            # If we get here, we're authenticated - proceed with scanning
            try:
                app.logger.info("Creating required Gmail labels")
                gmail_service.ensure_required_labels_exist()
                
                app.logger.info("Starting email scan")
                # Scan emails and process results, passing the current user's ID
                results = gmail_service.scan_and_process_emails(
                    days_to_scan=30,  # You can make this configurable if needed
                    user_id=current_user.id
                )
                scan_results = results if results else ["No new emails to process"]
                app.logger.info(f"Scan completed with results: {scan_results}")
                flash("Email scan completed successfully!", "success")
            except Exception as e:
                app.logger.error(f"Error during email scan: {str(e)}")
                flash(str(e), "error")
        except Exception as e:
            app.logger.error(f"Error with Gmail service: {str(e)}")
            flash(str(e), "error")
    
    return render_template(
        'scan_emails.html',
        credentials_exist=credentials_exist,
        token_exists=token_exists,
        scan_results=scan_results
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Only use debug mode in development
    app.run(host='0.0.0.0', port=8085) 