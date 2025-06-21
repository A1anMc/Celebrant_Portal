from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
from typing import Optional, cast
from forms import LoginForm, CoupleForm, CeremonyTemplateForm
from services.gmail_service import GmailService

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-please-change')

# Use DATABASE_URL for production database, fallback to SQLite for development
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    # Heroku provides DATABASE_URL starting with 'postgres://', but SQLAlchemy requires 'postgresql://'
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///celebrant.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # type: ignore

# Models
class User(UserMixin, db.Model):  # type: ignore
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(100), nullable=False)
    couples = db.relationship('Couple', backref='celebrant', lazy=True)
    templates = db.relationship('CeremonyTemplate', backref='celebrant', lazy=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

class CeremonyTemplate(db.Model):  # type: ignore
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)
    ceremony_type = db.Column(db.String(50))  # Civil, Religious, Custom
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    celebrant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Couple(db.Model):  # type: ignore
    id = db.Column(db.Integer, primary_key=True)
    partner1_name = db.Column(db.String(100), nullable=False)
    partner1_email = db.Column(db.String(120), nullable=False)
    partner1_phone = db.Column(db.String(20))
    partner2_name = db.Column(db.String(100), nullable=False)
    partner2_email = db.Column(db.String(120), nullable=False)
    partner2_phone = db.Column(db.String(20))
    ceremony_date = db.Column(db.DateTime)
    ceremony_location = db.Column(db.String(200))
    status = db.Column(db.String(20), default='Inquiry')  # Inquiry, Confirmed, Completed, Cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    celebrant_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ceremonies = db.relationship('Ceremony', backref='couple', lazy=True)
    documents = db.relationship('Document', backref='couple', lazy=True)

class Ceremony(db.Model):  # type: ignore
    id = db.Column(db.Integer, primary_key=True)
    couple_id = db.Column(db.Integer, db.ForeignKey('couple.id'), nullable=False)
    ceremony_type = db.Column(db.String(50))  # Civil, Religious, Custom
    template_content = db.Column(db.Text)
    custom_vows = db.Column(db.Text)
    readings = db.Column(db.Text)
    music = db.Column(db.Text)
    rehearsal_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    template_id = db.Column(db.Integer, db.ForeignKey('ceremony_template.id'))

class Document(db.Model):  # type: ignore
    id = db.Column(db.Integer, primary_key=True)
    couple_id = db.Column(db.Integer, db.ForeignKey('couple.id'), nullable=False)
    document_type = db.Column(db.String(50))  # Marriage Certificate, ID, etc.
    file_path = db.Column(db.String(200))
    status = db.Column(db.String(20))  # Pending, Received, Verified
    notes = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(id: str) -> Optional[User]:
    return User.query.get(int(id))

# Routes
@app.route('/')
@login_required
def index():
    upcoming_couples = Couple.query.filter_by(celebrant_id=current_user.id)\
        .filter(Couple.status != 'Completed')\
        .filter(Couple.status != 'Cancelled')\
        .order_by(Couple.ceremony_date)\
        .all()
    return render_template('index.html', couples=upcoming_couples)

@app.route('/login', methods=['GET', 'POST'])
def login():
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
    logout_user()
    return redirect(url_for('login'))

# Couple Management Routes
@app.route('/couples')
@login_required
def couples_list():
    couples = Couple.query.filter_by(celebrant_id=current_user.id)\
        .order_by(Couple.ceremony_date)\
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

@app.route('/templates/new', methods=['GET', 'POST'])
@login_required
def template_new():
    form = CeremonyTemplateForm()
    if form.validate_on_submit():
        template = CeremonyTemplate(  # type: ignore
            name=form.name.data,
            description=form.description.data,
            content=form.content.data,
            ceremony_type=form.ceremony_type.data,
            is_default=form.is_default.data,
            celebrant_id=current_user.id
        )
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

@app.route('/scan-emails', methods=['GET', 'POST'])
@login_required
def scan_emails():
    if request.method == 'POST':
        try:
            days = int(request.form.get('days', 30))
            gmail_service = GmailService()
            couples_data = gmail_service.scan_for_couples(days)
            
            # Process and store the found couples
            for couple_data in couples_data:
                # Check if couple already exists based on email
                existing_couple = None
                for email in couple_data['potential_emails']:
                    existing_couple = Couple.query.filter(
                        (Couple.partner1_email == email) | 
                        (Couple.partner2_email == email)
                    ).first()
                    if existing_couple:
                        break
                
                if not existing_couple:
                    # Create new couple with required fields
                    couple = Couple(
                        partner1_name="[Name Pending]",  # Required field
                        partner2_name="[Name Pending]",  # Required field
                        partner1_email=couple_data['potential_emails'][0] if couple_data['potential_emails'] else None,
                        partner2_email=couple_data['potential_emails'][1] if len(couple_data['potential_emails']) > 1 else None,
                        partner1_phone=couple_data['potential_phones'][0] if couple_data['potential_phones'] else None,
                        partner2_phone=couple_data['potential_phones'][1] if len(couple_data['potential_phones']) > 1 else None,
                        status="Inquiry",  # Default status for imported couples
                        ceremony_date=datetime.strptime(couple_data['potential_dates'][0], '%Y-%m-%d') if couple_data['potential_dates'] else None,
                        ceremony_location=couple_data['potential_locations'][0] if couple_data['potential_locations'] else None,
                        notes=f"Imported from email:\nSubject: {couple_data['subject']}\nReceived on: {couple_data['date_received']}\n\nRaw email content:\n{couple_data['raw_body'][:500]}...",
                        celebrant_id=current_user.id  # Add the celebrant_id
                    )
                    db.session.add(couple)
            
            db.session.commit()
            flash(f'Successfully processed {len(couples_data)} emails', 'success')
            
        except Exception as e:
            flash(f'Error scanning emails: {str(e)}', 'error')
            return redirect(url_for('scan_emails'))
        
        return redirect(url_for('couples_list'))
    
    return render_template('scan_emails.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Only use debug mode in development
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False) 