# Standard library imports
import io
import os
import logging
from datetime import datetime
from typing import Optional, Any
import csv
import json
import time
from functools import wraps

# Third-party imports
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, Text, Boolean, DateTime, Date, Float
from sqlalchemy.orm import relationship
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
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

# Initialize Celery
from celery_app import make_celery
celery = make_celery(app)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('celebrant_portal.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Error handling decorator
def handle_db_errors(f):
    """Decorator to handle database errors consistently."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f"Database integrity error in {f.__name__}: {str(e)}")
            flash('A database error occurred. Please check for duplicate entries.', 'error')
            return redirect(request.referrer or url_for('index'))
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error in {f.__name__}: {str(e)}")
            flash('A database error occurred. Please try again.', 'error')
            return redirect(request.referrer or url_for('index'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Unexpected error in {f.__name__}: {str(e)}")
            flash('An unexpected error occurred. Please try again.', 'error')
            return redirect(request.referrer or url_for('index'))
    return decorated_function

# Models
class User(UserMixin, db.Model):
    """User model for authentication."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    email = Column(String(120), unique=True, nullable=True)
    name = Column(String(100), nullable=True)
    is_admin = Column(Boolean, default=False, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add indexes for performance
    __table_args__ = (
        db.Index('idx_user_email', 'email'),
        db.Index('idx_user_username', 'username'),
    )
    
    # Relationships
    couples = relationship('Couple', back_populates='celebrant')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Couple(db.Model):
    """Model for couples getting married."""
    __tablename__ = 'couples'
    
    id = Column(Integer, primary_key=True)
    partner1_name = Column(String(100), nullable=False)
    partner1_email = Column(String(120), nullable=True)
    partner1_phone = Column(String(20), nullable=True)
    partner2_name = Column(String(100), nullable=False)
    partner2_email = Column(String(120), nullable=True)
    partner2_phone = Column(String(20), nullable=True)
    ceremony_date = Column(Date, nullable=True)
    ceremony_time = Column(String(50), nullable=True)
    ceremony_location = Column(String(200), nullable=True)
    ceremony_type = Column(String(50), nullable=True)
    guest_count = Column(Integer, nullable=True)
    package = Column(String(50), nullable=True)
    fee = Column(Float, nullable=True)
    travel_fee = Column(Float, nullable=True)
    vows = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String(50), default='Inquiry')
    confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    celebrant_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    template_id = Column(Integer, ForeignKey('ceremony_templates.id'), nullable=True)
    
    # Add indexes for performance
    __table_args__ = (
        db.Index('idx_partner_names', 'partner1_name', 'partner2_name'),
        db.Index('idx_ceremony_date', 'ceremony_date'),
        db.Index('idx_couple_status', 'status'),
        db.Index('idx_couple_celebrant', 'celebrant_id'),
        db.Index('idx_partner_emails', 'partner1_email', 'partner2_email'),
    )
    
    # Relationships
    celebrant = relationship('User', back_populates='couples')
    template = relationship('CeremonyTemplate', back_populates='couples')

class CeremonyTemplate(db.Model):
    """Model for ceremony templates."""
    __tablename__ = 'ceremony_templates'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    ceremony_type = Column(String(50), nullable=True)
    is_default = Column(Boolean, default=False, nullable=True)
    celebrant_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add indexes for performance
    __table_args__ = (
        db.Index('idx_template_type', 'ceremony_type'),
        db.Index('idx_template_name', 'name'),
        db.Index('idx_template_celebrant', 'celebrant_id'),
    )
    
    # Relationships
    couples = relationship('Couple', back_populates='template')
    celebrant = relationship('User', backref='templates')

class ImportedName(db.Model):
    """Model for storing imported names to scan for."""
    __tablename__ = 'imported_names'
    
    id = Column(Integer, primary_key=True)
    partner1_name = Column(String(100), nullable=True)
    partner2_name = Column(String(100), nullable=True)
    ceremony_date = Column(Date, nullable=True)
    location = Column(String(255), nullable=True)
    guest_count = Column(String(50), nullable=True)
    ceremony_time = Column(String(50), nullable=True)
    role = Column(String(100), nullable=True)
    package = Column(String(100), nullable=True)
    fee = Column(String(100), nullable=True)
    travel_fee = Column(String(100), nullable=True)
    vows = Column(String(100), nullable=True)
    confirmed = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    is_processed = Column(Boolean, default=False, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add indexes for performance
    __table_args__ = (
        db.Index('idx_imported_names', 'partner1_name', 'partner2_name'),
        db.Index('idx_imported_processed', 'is_processed'),
        db.Index('idx_imported_date', 'ceremony_date'),
    )

class ImportSession(db.Model):
    """Model for tracking CSV import sessions."""
    __tablename__ = 'import_sessions'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    total_rows = Column(Integer, nullable=False)
    processed_rows = Column(Integer, default=0)
    chunk_size = Column(Integer, default=100)
    current_chunk = Column(Integer, default=0)
    status = Column(String(50), default='pending')  # pending, processing, paused, completed, failed
    error_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    column_mapping = Column(Text, nullable=True)  # JSON string of column mappings
    errors = Column(Text, nullable=True)  # JSON string of errors
    
    # Add indexes for performance
    __table_args__ = (
        db.Index('idx_import_status', 'status'),
        db.Index('idx_import_created', 'created_at'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'total_rows': self.total_rows,
            'processed_rows': self.processed_rows,
            'chunk_size': self.chunk_size,
            'current_chunk': self.current_chunk,
            'status': self.status,
            'error_count': self.error_count,
            'progress_percentage': (self.processed_rows / self.total_rows * 100) if self.total_rows > 0 else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

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
@handle_db_errors
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
        logger.info(f"New couple created: {couple.partner1_name} & {couple.partner2_name}")
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
@handle_db_errors
def couple_edit(id: int):
    couple = Couple.query.filter_by(id=id, celebrant_id=current_user.id).first_or_404()
    form = CoupleForm(obj=couple)
    
    if form.validate_on_submit():
        form.populate_obj(couple)  # type: ignore
        db.session.commit()
        logger.info(f"Couple updated: {couple.partner1_name} & {couple.partner2_name}")
        flash('Couple updated successfully!', 'success')
        return redirect(url_for('couple_view', id=id))
    
    return render_template('couples/edit.html', couple=couple, form=form)

@app.route('/couples/<int:id>/delete', methods=['POST'])
@login_required
@handle_db_errors
def couple_delete(id: int):
    couple = Couple.query.filter_by(id=id, celebrant_id=current_user.id).first_or_404()
    couple_names = f"{couple.partner1_name} & {couple.partner2_name}"
    db.session.delete(couple)
    db.session.commit()
    logger.info(f"Couple deleted: {couple_names}")
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
@handle_db_errors
def template_new():
    form = CeremonyTemplateForm()
    if form.validate_on_submit():
        # Handle file upload if provided
        uploaded_content = handle_template_upload(form)
        
        template = CeremonyTemplate(
            name=form.name.data,
            description=form.description.data,
            content=uploaded_content or form.content.data,  # Use uploaded content if available
            ceremony_type=form.ceremony_type.data,
            is_default=form.is_default.data,
            celebrant_id=current_user.id
        )
        
        # If this is set as default, unset other defaults of the same type
        if template.is_default:
            CeremonyTemplate.query.filter_by(
                celebrant_id=current_user.id,
                ceremony_type=template.ceremony_type,
                is_default=True
            ).update({'is_default': False})
        
        db.session.add(template)
        db.session.commit()
        logger.info(f"New template created: {template.name}")
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
@handle_db_errors
def template_edit(id: int):
    template = CeremonyTemplate.query.filter_by(id=id, celebrant_id=current_user.id).first_or_404()
    form = CeremonyTemplateForm(obj=template)
    
    if form.validate_on_submit():
        # Handle file upload if provided
        uploaded_content = handle_template_upload(form)
        if uploaded_content:
            template.content = uploaded_content
        
        # Update other fields
        template.name = form.name.data
        template.description = form.description.data
        template.ceremony_type = form.ceremony_type.data
        
        # Handle default template logic
        if form.is_default.data and not template.is_default:
            # Unset other defaults of the same type
            CeremonyTemplate.query.filter_by(
                celebrant_id=current_user.id,
                ceremony_type=template.ceremony_type,
                is_default=True
            ).filter(CeremonyTemplate.id != template.id).update({'is_default': False})
        
        template.is_default = form.is_default.data
        if not uploaded_content:  # Only update content if no file was uploaded
            template.content = form.content.data
            
        db.session.commit()
        logger.info(f"Template updated: {template.name}")
        flash('Template updated successfully!', 'success')
        return redirect(url_for('template_view', id=id))
    
    return render_template('templates/edit.html', template=template, form=form)

@app.route('/templates/<int:id>/delete', methods=['POST'])
@login_required
@handle_db_errors
def template_delete(id: int):
    template = CeremonyTemplate.query.filter_by(id=id, celebrant_id=current_user.id).first_or_404()
    template_name = template.name
    db.session.delete(template)
    db.session.commit()
    logger.info(f"Template deleted: {template_name}")
    flash('Template deleted successfully!', 'success')
    return redirect(url_for('templates_list'))

# Google Drive Template Import Routes
@app.route('/templates/import')
@login_required
def templates_import():
    """Show the Drive template import page."""
    try:
        from services.drive_service import DriveService
        drive_service = DriveService()
        drive_connected = drive_service.check_drive_access()
    except Exception:
        drive_connected = False
    
    return render_template('templates/import.html', 
                         drive_connected=drive_connected,
                         files=None, 
                         searched=False)

@app.route('/templates/authorize-drive')
@login_required
def authorize_drive():
    """Start the Drive authorization process."""
    try:
        from services.drive_service import DriveService
        drive_service = DriveService()
        
        # Force re-authentication to get Drive scope
        if os.path.exists('token.pickle'):
            os.remove('token.pickle')
        
        # This will trigger the OAuth flow
        drive_service.ensure_authenticated()
        
        flash('Google Drive access authorized successfully!', 'success')
        return redirect(url_for('templates_import'))
        
    except Exception as e:
        logger.error(f"Drive authorization error: {e}")
        flash(f'Failed to authorize Drive access: {str(e)}', 'error')
        return redirect(url_for('templates_import'))

@app.route('/templates/search-drive-templates')
@login_required
def search_drive_templates():
    """Search for templates in Google Drive."""
    try:
        from services.drive_service import DriveService
        drive_service = DriveService()
        
        folder_name = request.args.get('folder')
        files = drive_service.search_template_files(folder_name=folder_name)
        
        return jsonify({
            'success': True,
            'files': files
        })
        
    except Exception as e:
        logger.error(f"Drive search error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/templates/preview-drive-file')
@login_required
def preview_drive_file():
    """Preview a Drive file."""
    try:
        from services.drive_service import DriveService
        drive_service = DriveService()
        
        file_id = request.args.get('file_id')
        if not file_id:
            return jsonify({
                'success': False,
                'error': 'File ID is required'
            })
        
        preview_data = drive_service.preview_file(file_id)
        
        return jsonify({
            'success': True,
            'metadata': preview_data['metadata'],
            'preview': preview_data['preview']
        })
        
    except Exception as e:
        logger.error(f"Drive preview error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/templates/import-from-drive', methods=['POST'])
@login_required
@handle_db_errors
def import_from_drive():
    """Import a template from Google Drive."""
    try:
        from services.drive_service import DriveService
        drive_service = DriveService()
        
        file_id = request.form.get('file_id')
        name = request.form.get('name')
        template_type = request.form.get('type')
        description = request.form.get('description', '')
        is_default = request.form.get('is_default') == 'on'
        
        if not file_id or not name or not template_type:
            flash('Missing required fields', 'error')
            return redirect(url_for('templates_import'))
        
        # Get the file content
        file_data = drive_service.get_file_content(file_id)
        
        # Create the template
        template = CeremonyTemplate(
            name=name,
            description=description,
            content=file_data['processed_content'],
            ceremony_type=template_type,
            is_default=is_default,
            celebrant_id=current_user.id
        )
        
        # If this is set as default, unset other defaults of the same type
        if template.is_default:
            CeremonyTemplate.query.filter_by(
                celebrant_id=current_user.id,
                ceremony_type=template.ceremony_type,
                is_default=True
            ).update({'is_default': False})
        
        db.session.add(template)
        db.session.commit()
        
        logger.info(f"Template imported from Drive: {template.name}")
        flash(f'Template "{name}" imported successfully from Google Drive!', 'success')
        
        return redirect(url_for('template_view', id=template.id))
        
    except Exception as e:
        logger.error(f"Drive import error: {e}")
        flash(f'Failed to import template: {str(e)}', 'error')
        return redirect(url_for('templates_import'))

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

@app.route('/import-names', methods=['GET'])
@login_required
def import_names():
    """Show the enhanced import interface."""
    return render_template('import_names_enhanced.html')

# Import API Routes
@app.route('/api/import/upload', methods=['POST'])
@login_required
def api_import_upload():
    """Handle file upload and create import session."""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'})
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'})
        
    if not file.filename.endswith('.csv'):
        return jsonify({'success': False, 'error': 'File must be a CSV'})
    
    try:
        # Save file temporarily
        temp_path = os.path.join(app.instance_path, f'import_{int(time.time())}.csv')
        os.makedirs(app.instance_path, exist_ok=True)
        file.save(temp_path)
        
        # Read CSV headers and preview data
        with open(temp_path, 'r') as f:
            csv_reader = csv.reader(f)
            headers = next(csv_reader)
            preview_data = []
            for _ in range(10):  # Get 10 rows for preview
                try:
                    row = next(csv_reader)
                    preview_data.append(dict(zip(headers, row)))
                except StopIteration:
                    break
            
            # Count total rows
            f.seek(0)
            total_rows = sum(1 for _ in f) - 1  # Subtract header row
        
        # Create import session
        chunk_size = int(request.form.get('chunkSize', 100))
        session = ImportSession(
            filename=os.path.basename(temp_path),
            total_rows=total_rows,
            chunk_size=chunk_size
        )
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'session': session.to_dict(),
            'columns': headers,
            'preview_data': preview_data
        })
        
    except Exception as e:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/import/map-columns', methods=['POST'])
@login_required
def api_import_map_columns():
    """Save column mappings for an import session."""
    data = request.get_json()
    if not data or 'session_id' not in data or 'mappings' not in data:
        return jsonify({'success': False, 'error': 'Invalid request data'})
    
    try:
        session = ImportSession.query.get(data['session_id'])
        if not session:
            return jsonify({'success': False, 'error': 'Import session not found'})
        
        # Validate required mappings
        required_fields = {'Couple', 'Date'}
        mapped_fields = set(data['mappings'].values())
        missing_fields = required_fields - mapped_fields
        if missing_fields:
            return jsonify({
                'success': False, 
                'error': f'Missing required field mappings: {", ".join(missing_fields)}'
            })
        
        # Save mappings
        session.column_mapping = json.dumps(data['mappings'])
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/import/start', methods=['POST'])
@login_required
def api_import_start():
    """Start or resume the import process."""
    data = request.get_json()
    if not data or 'session_id' not in data:
        return jsonify({'success': False, 'error': 'Invalid request data'})
    
    try:
        session = ImportSession.query.get(data['session_id'])
        if not session:
            return jsonify({'success': False, 'error': 'Import session not found'})
        
        if session.status not in ['pending', 'paused']:
            return jsonify({'success': False, 'error': f'Cannot start import in {session.status} status'})
        
        # Start background task
        import_task.delay(session.id)
        
        session.status = 'processing'
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/import/pause', methods=['POST'])
@login_required
def api_import_pause():
    """Pause or resume the import process."""
    data = request.get_json()
    if not data or 'session_id' not in data:
        return jsonify({'success': False, 'error': 'Invalid request data'})
    
    try:
        session = ImportSession.query.get(data['session_id'])
        if not session:
            return jsonify({'success': False, 'error': 'Import session not found'})
        
        if session.status == 'processing':
            session.status = 'paused'
        elif session.status == 'paused':
            session.status = 'processing'
            import_task.delay(session.id)
        else:
            return jsonify({'success': False, 'error': f'Cannot pause/resume import in {session.status} status'})
        
        db.session.commit()
        return jsonify({'success': True, 'status': session.status})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/import/cancel', methods=['POST'])
@login_required
def api_import_cancel():
    """Cancel the import process."""
    data = request.get_json()
    if not data or 'session_id' not in data:
        return jsonify({'success': False, 'error': 'Invalid request data'})
    
    try:
        session = ImportSession.query.get(data['session_id'])
        if not session:
            return jsonify({'success': False, 'error': 'Import session not found'})
        
        if session.status in ['completed', 'failed']:
            return jsonify({'success': False, 'error': f'Cannot cancel import in {session.status} status'})
        
        # Clean up temp file
        temp_path = os.path.join(app.instance_path, session.filename)
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        session.status = 'failed'
        session.errors = json.dumps(['Import cancelled by user'])
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/import/status/<int:session_id>')
@login_required
def api_import_status(session_id):
    """Get the current status of an import session."""
    try:
        session = ImportSession.query.get(session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Import session not found'})
        
        return jsonify(session.to_dict())
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Export Routes
@app.route('/api/export/couples', methods=['GET'])
@login_required
def export_couples():
    """Export couples data to CSV."""
    try:
        # Get filter parameters
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = Couple.query
        
        if status:
            query = query.filter_by(status=status)
        if start_date:
            query = query.filter(Couple.ceremony_date >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            query = query.filter(Couple.ceremony_date <= datetime.strptime(end_date, '%Y-%m-%d'))
            
        couples = query.order_by(Couple.ceremony_date).all()
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        headers = [
            'Partner 1 Name', 'Partner 1 Email', 'Partner 1 Phone',
            'Partner 2 Name', 'Partner 2 Email', 'Partner 2 Phone',
            'Ceremony Date', 'Ceremony Time', 'Ceremony Location',
            'Ceremony Type', 'Status', 'Notes'
        ]
        writer.writerow(headers)
        
        # Write data
        for couple in couples:
            writer.writerow([
                couple.partner1_name,
                couple.partner1_email,
                couple.partner1_phone,
                couple.partner2_name,
                couple.partner2_email,
                couple.partner2_phone,
                couple.ceremony_date.strftime('%Y-%m-%d') if couple.ceremony_date else '',
                couple.ceremony_time,
                couple.ceremony_location,
                couple.ceremony_type,
                couple.status,
                couple.notes
            ])
        
        # Prepare response
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=couples.csv',
                'Content-Type': 'text/csv'
            }
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/export/email-scan', methods=['GET'])
@login_required
def export_email_scan():
    """Export email scan results."""
    try:
        # Get filter parameters
        days = int(request.args.get('days', 30))
        include_processed = request.args.get('include_processed', 'false').lower() == 'true'
        
        # Get imported names
        query = ImportedName.query
        if not include_processed:
            query = query.filter_by(is_processed=False)
        imported_names = query.all()
        
        # Initialize Gmail service
        gmail_service = GmailService()
        
        # Scan emails for each couple
        results = []
        for imported_name in imported_names:
            # Create search query
            name_queries = []
            for name in [imported_name.partner1_name, imported_name.partner2_name]:
                if name:
                    name_queries.append(f'"{name}"')
            
            query = f'in:sent newer_than:{days}d ({" OR ".join(name_queries)})'
            emails = gmail_service.search_emails(query)
            
            for email in emails:
                email_info = gmail_service.extract_email_info(email)
                if email_info:
                    results.append({
                        'couple': f"{imported_name.partner1_name} & {imported_name.partner2_name}",
                        'subject': email_info['subject'],
                        'date': email['internalDate'],
                        'content': email_info['content'],
                        'needs_response': email_info['needs_response'],
                        'is_confirmation': email_info['is_confirmation']
                    })
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        headers = ['Couple', 'Subject', 'Date', 'Content', 'Needs Response', 'Is Confirmation']
        writer.writerow(headers)
        
        # Write data
        for result in results:
            writer.writerow([
                result['couple'],
                result['subject'],
                datetime.fromtimestamp(int(result['date'])/1000).strftime('%Y-%m-%d %H:%M:%S'),
                result['content'],
                'Yes' if result['needs_response'] else 'No',
                'Yes' if result['is_confirmation'] else 'No'
            ])
        
        # Prepare response
        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=email_scan.csv',
                'Content-Type': 'text/csv'
            }
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/export/report', methods=['GET'])
@login_required
def export_report():
    """Generate and export a comprehensive report."""
    try:
        # Get filter parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Initialize report data
        report = {
            'generated_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
            'date_range': f"{start_date} to {end_date}" if start_date and end_date else 'All time',
            'summary': {},
            'status_breakdown': {},
            'location_breakdown': {},
            'ceremony_type_breakdown': {},
            'upcoming_ceremonies': [],
            'needs_attention': []
        }
        
        # Build base query
        query = Couple.query
        if start_date:
            query = query.filter(Couple.ceremony_date >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            query = query.filter(Couple.ceremony_date <= datetime.strptime(end_date, '%Y-%m-%d'))
        
        # Get all relevant couples
        couples = query.all()
        
        # Calculate summary statistics
        report['summary'] = {
            'total_couples': len(couples),
            'upcoming_ceremonies': len([c for c in couples if c.ceremony_date and c.ceremony_date > datetime.utcnow().date()]),
            'completed_ceremonies': len([c for c in couples if c.status == 'Completed']),
            'pending_confirmations': len([c for c in couples if c.status == 'Pending'])
        }
        
        # Calculate status breakdown
        status_counts = {}
        for couple in couples:
            status_counts[couple.status] = status_counts.get(couple.status, 0) + 1
        report['status_breakdown'] = status_counts
        
        # Calculate location breakdown
        location_counts = {}
        for couple in couples:
            if couple.ceremony_location:
                location_counts[couple.ceremony_location] = location_counts.get(couple.ceremony_location, 0) + 1
        report['location_breakdown'] = location_counts
        
        # Calculate ceremony type breakdown
        type_counts = {}
        for couple in couples:
            if couple.ceremony_type:
                type_counts[couple.ceremony_type] = type_counts.get(couple.ceremony_type, 0) + 1
        report['ceremony_type_breakdown'] = type_counts
        
        # Get upcoming ceremonies
        upcoming = [c for c in couples if c.ceremony_date and c.ceremony_date > datetime.utcnow().date()]
        upcoming.sort(key=lambda x: x.ceremony_date)
        report['upcoming_ceremonies'] = [{
            'couple': f"{c.partner1_name} & {c.partner2_name}",
            'date': c.ceremony_date.strftime('%Y-%m-%d'),
            'location': c.ceremony_location,
            'status': c.status
        } for c in upcoming[:10]]  # Show next 10 ceremonies
        
        # Get couples needing attention
        needs_attention = [c for c in couples if c.status in ['Pending', 'Inquiry'] or not c.ceremony_date]
        report['needs_attention'] = [{
            'couple': f"{c.partner1_name} & {c.partner2_name}",
            'status': c.status,
            'missing_info': [
                'Ceremony Date' if not c.ceremony_date else None,
                'Location' if not c.ceremony_location else None,
                'Contact Info' if not (c.partner1_email or c.partner2_email) else None
            ]
        } for c in needs_attention]
        
        # Convert to JSON
        return jsonify(report)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Health Check and Monitoring Endpoints
@app.route('/api/health')
def health_check():
    """Basic health check endpoint."""
    try:
        # Test database connectivity
        user_count = User.query.count()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected',
            'users': user_count
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 500

@app.route('/api/stats')
@login_required
def get_stats():
    """Get application statistics."""
    try:
        stats = {
            'couples': {
                'total': Couple.query.filter_by(celebrant_id=current_user.id).count(),
                'confirmed': Couple.query.filter_by(celebrant_id=current_user.id, status='Confirmed').count(),
                'completed': Couple.query.filter_by(celebrant_id=current_user.id, status='Completed').count(),
                'inquiries': Couple.query.filter_by(celebrant_id=current_user.id, status='Inquiry').count(),
                'cancelled': Couple.query.filter_by(celebrant_id=current_user.id, status='Cancelled').count()
            },
            'templates': {
                'total': CeremonyTemplate.query.filter_by(celebrant_id=current_user.id).count(),
                'default': CeremonyTemplate.query.filter_by(celebrant_id=current_user.id, is_default=True).count()
            },
            'imports': {
                'total_sessions': ImportSession.query.count(),
                'active_sessions': ImportSession.query.filter(ImportSession.status.in_(['processing', 'paused'])).count(),
                'unprocessed_names': ImportedName.query.filter_by(is_processed=False).count()
            }
        }
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Stats retrieval failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    logger.warning(f"404 error: {request.url}")
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Not found'}), 404
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    db.session.rollback()
    logger.error(f"500 error: {str(error)}")
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden_error(error):
    """Handle 403 errors."""
    logger.warning(f"403 error: {request.url}")
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Forbidden'}), 403
    return render_template('errors/403.html'), 403

# Register legal forms blueprint
try:
    from legal_forms_routes import legal_forms_bp
    app.register_blueprint(legal_forms_bp, url_prefix='/legal-forms')
    logger.info("Legal forms blueprint registered successfully")
except ImportError as e:
    logger.warning(f"Could not register legal forms blueprint: {e}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Only use debug mode in development
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=8085, debug=debug_mode) 