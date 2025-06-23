# Standard library imports
import io
import os
import logging
from datetime import datetime, timedelta, date
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
from flask_cors import CORS

# Local imports
from config import config
from forms import LoginForm, CoupleForm, CeremonyTemplateForm
from services.gmail_service import GmailService
from models import db, User, Couple, CeremonyTemplate, ImportedName, ImportSession, Organization

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for React frontend
CORS(app, origins=['http://localhost:3000'], supports_credentials=True)

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
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Global context processor to inject 'today' into all templates
@app.context_processor
def inject_today():
    """Inject today's date into all templates."""
    return {'today': datetime.today().date()}

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

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return db.session.get(User, int(user_id))

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
        # Find user by email (across all organizations for now)
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            if user.is_active:
                login_user(user)
                logger.info(f"User logged in: {user.email}")
                return redirect(url_for('index'))
            else:
                flash('Account is deactivated. Please contact administrator.')
        else:
            flash('Invalid email or password')
            logger.warning(f"Failed login attempt for email: {form.email.data}")
    elif form.errors:
        # Log form validation errors
        logger.warning(f"Form validation errors: {form.errors}")
    
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
            ).update({'is_default': False})
        
        template.is_default = form.is_default.data
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
    """Get dashboard statistics."""
    try:
        # Get counts for current user's organization
        total_couples = Couple.query.filter_by(celebrant_id=current_user.id).count()
        upcoming_couples = Couple.query.filter_by(celebrant_id=current_user.id)\
            .filter(Couple.status.in_(['Confirmed', 'Inquiry']))\
            .filter(Couple.ceremony_date >= datetime.now().date())\
            .count()
        completed_couples = Couple.query.filter_by(celebrant_id=current_user.id)\
            .filter(Couple.status == 'Completed')\
            .count()
        total_templates = CeremonyTemplate.query.filter_by(celebrant_id=current_user.id).count()
        
        # Get upcoming ceremonies (next 30 days)
        thirty_days_from_now = datetime.now().date() + timedelta(days=30)
        upcoming_ceremonies = Couple.query.filter_by(celebrant_id=current_user.id)\
            .filter(Couple.ceremony_date >= datetime.now().date())\
            .filter(Couple.ceremony_date <= thirty_days_from_now)\
            .filter(Couple.status.in_(['Confirmed', 'Inquiry']))\
            .order_by(Couple.ceremony_date.asc())\
            .limit(5)\
            .all()
        
        return jsonify({
            'success': True,
            'data': {
                'total_couples': total_couples,
                'upcoming_couples': upcoming_couples,
                'completed_couples': completed_couples,
                'total_templates': total_templates,
                'upcoming_ceremonies': [
                    {
                        'id': couple.id,
                        'partner1_name': couple.partner1_name,
                        'partner2_name': couple.partner2_name,
                        'ceremony_date': couple.ceremony_date.isoformat() if couple.ceremony_date else None,
                        'ceremony_location': couple.ceremony_location,
                        'status': couple.status
                    }
                    for couple in upcoming_ceremonies
                ]
            }
        })
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get statistics'}), 500

# API endpoints for React frontend
@app.route('/api/couples', methods=['GET'])
@login_required
def api_get_couples():
    """Get couples as JSON for React frontend."""
    try:
        status = request.args.get('status')
        search = request.args.get('search')
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        query = Couple.query.filter_by(celebrant_id=current_user.id)
        
        if status:
            query = query.filter(Couple.status == status)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Couple.partner1_name.ilike(search_term),
                    Couple.partner2_name.ilike(search_term),
                    Couple.ceremony_location.ilike(search_term)
                )
            )
        
        couples = query.order_by(Couple.ceremony_date.asc()).paginate(
            page=page, per_page=limit, error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': [
                {
                    'id': couple.id,
                    'partner1_name': couple.partner1_name,
                    'partner1_email': couple.partner1_email,
                    'partner1_phone': couple.partner1_phone,
                    'partner2_name': couple.partner2_name,
                    'partner2_email': couple.partner2_email,
                    'partner2_phone': couple.partner2_phone,
                    'ceremony_date': couple.ceremony_date.isoformat() if couple.ceremony_date else None,
                    'ceremony_time': couple.ceremony_time,
                    'ceremony_location': couple.ceremony_location,
                    'ceremony_type': couple.ceremony_type,
                    'guest_count': couple.guest_count,
                    'package': couple.package,
                    'fee': couple.fee,
                    'travel_fee': couple.travel_fee,
                    'vows': couple.vows,
                    'notes': couple.notes,
                    'status': couple.status,
                    'confirmed': couple.confirmed,
                    'created_at': couple.created_at.isoformat() if couple.created_at else None,
                    'updated_at': couple.updated_at.isoformat() if couple.updated_at else None
                }
                for couple in couples.items
            ],
            'pagination': {
                'page': page,
                'per_page': limit,
                'total': couples.total,
                'pages': couples.pages
            }
        })
    except Exception as e:
        logger.error(f"Error getting couples: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get couples'}), 500

@app.route('/api/couples/<int:id>', methods=['GET'])
@login_required
def api_get_couple(id):
    """Get a single couple as JSON."""
    try:
        couple = Couple.query.filter_by(id=id, celebrant_id=current_user.id).first()
        if not couple:
            return jsonify({'success': False, 'error': 'Couple not found'}), 404
        
        return jsonify({
            'success': True,
            'data': {
                'id': couple.id,
                'partner1_name': couple.partner1_name,
                'partner1_email': couple.partner1_email,
                'partner1_phone': couple.partner1_phone,
                'partner2_name': couple.partner2_name,
                'partner2_email': couple.partner2_email,
                'partner2_phone': couple.partner2_phone,
                'ceremony_date': couple.ceremony_date.isoformat() if couple.ceremony_date else None,
                'ceremony_time': couple.ceremony_time,
                'ceremony_location': couple.ceremony_location,
                'ceremony_type': couple.ceremony_type,
                'guest_count': couple.guest_count,
                'package': couple.package,
                'fee': couple.fee,
                'travel_fee': couple.travel_fee,
                'vows': couple.vows,
                'notes': couple.notes,
                'status': couple.status,
                'confirmed': couple.confirmed,
                'created_at': couple.created_at.isoformat() if couple.created_at else None,
                'updated_at': couple.updated_at.isoformat() if couple.updated_at else None
            }
        })
    except Exception as e:
        logger.error(f"Error getting couple {id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get couple'}), 500

@app.route('/api/couples', methods=['POST'])
@login_required
def api_create_couple():
    """Create a new couple via API."""
    try:
        data = request.get_json()
        
        couple = Couple(
            partner1_name=data['partner1_name'],
            partner1_email=data.get('partner1_email'),
            partner1_phone=data.get('partner1_phone'),
            partner2_name=data['partner2_name'],
            partner2_email=data.get('partner2_email'),
            partner2_phone=data.get('partner2_phone'),
            ceremony_date=datetime.strptime(data['ceremony_date'], '%Y-%m-%d').date() if data.get('ceremony_date') else None,
            ceremony_time=data.get('ceremony_time'),
            ceremony_location=data.get('ceremony_location'),
            ceremony_type=data.get('ceremony_type'),
            guest_count=data.get('guest_count'),
            package=data.get('package'),
            fee=data.get('fee'),
            travel_fee=data.get('travel_fee'),
            vows=data.get('vows'),
            notes=data.get('notes'),
            status=data.get('status', 'Inquiry'),
            confirmed=data.get('confirmed', False),
            celebrant_id=current_user.id
        )
        
        db.session.add(couple)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'id': couple.id,
                'partner1_name': couple.partner1_name,
                'partner2_name': couple.partner2_name,
                'status': couple.status
            }
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating couple: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to create couple'}), 500

@app.route('/api/couples/<int:id>', methods=['PUT'])
@login_required
def api_update_couple(id):
    """Update a couple via API."""
    try:
        couple = Couple.query.filter_by(id=id, celebrant_id=current_user.id).first()
        if not couple:
            return jsonify({'success': False, 'error': 'Couple not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        for field, value in data.items():
            if hasattr(couple, field):
                if field == 'ceremony_date' and value:
                    setattr(couple, field, datetime.strptime(value, '%Y-%m-%d').date())
                else:
                    setattr(couple, field, value)
        
        couple.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True, 'data': {'id': couple.id}})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating couple {id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to update couple'}), 500

@app.route('/api/couples/<int:id>', methods=['DELETE'])
@login_required
def api_delete_couple(id):
    """Delete a couple via API."""
    try:
        couple = Couple.query.filter_by(id=id, celebrant_id=current_user.id).first()
        if not couple:
            return jsonify({'success': False, 'error': 'Couple not found'}), 404
        
        db.session.delete(couple)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting couple {id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to delete couple'}), 500

@app.route('/api/templates', methods=['GET'])
@login_required
def api_get_templates():
    """Get templates as JSON for React frontend."""
    try:
        ceremony_type = request.args.get('ceremony_type')
        search = request.args.get('search')
        
        query = CeremonyTemplate.query.filter_by(celebrant_id=current_user.id)
        
        if ceremony_type:
            query = query.filter(CeremonyTemplate.ceremony_type == ceremony_type)
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    CeremonyTemplate.name.ilike(search_term),
                    CeremonyTemplate.description.ilike(search_term)
                )
            )
        
        templates = query.order_by(CeremonyTemplate.name.asc()).all()
        
        return jsonify({
            'success': True,
            'data': [
                {
                    'id': template.id,
                    'name': template.name,
                    'description': template.description,
                    'content': template.content,
                    'ceremony_type': template.ceremony_type,
                    'is_default': template.is_default,
                    'created_at': template.created_at.isoformat() if template.created_at else None,
                    'updated_at': template.updated_at.isoformat() if template.updated_at else None
                }
                for template in templates
            ]
        })
    except Exception as e:
        logger.error(f"Error getting templates: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get templates'}), 500

@app.route('/api/templates/<int:id>', methods=['GET'])
@login_required
def api_get_template(id):
    """Get a single template as JSON."""
    try:
        template = CeremonyTemplate.query.filter_by(id=id, celebrant_id=current_user.id).first()
        if not template:
            return jsonify({'success': False, 'error': 'Template not found'}), 404
        
        return jsonify({
            'success': True,
            'data': {
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'content': template.content,
                'ceremony_type': template.ceremony_type,
                'is_default': template.is_default,
                'created_at': template.created_at.isoformat() if template.created_at else None,
                'updated_at': template.updated_at.isoformat() if template.updated_at else None
            }
        })
    except Exception as e:
        logger.error(f"Error getting template {id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get template'}), 500

@app.route('/api/templates', methods=['POST'])
@login_required
def api_create_template():
    """Create a new template via API."""
    try:
        data = request.get_json()
        
        template = CeremonyTemplate(
            name=data['name'],
            description=data.get('description'),
            content=data['content'],
            ceremony_type=data.get('ceremony_type'),
            is_default=data.get('is_default', False),
            celebrant_id=current_user.id
        )
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'id': template.id,
                'name': template.name
            }
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating template: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to create template'}), 500

@app.route('/api/templates/<int:id>', methods=['PUT'])
@login_required
def api_update_template(id):
    """Update a template via API."""
    try:
        template = CeremonyTemplate.query.filter_by(id=id, celebrant_id=current_user.id).first()
        if not template:
            return jsonify({'success': False, 'error': 'Template not found'}), 404
        
        data = request.get_json()
        
        # Update fields
        for field, value in data.items():
            if hasattr(template, field):
                setattr(template, field, value)
        
        template.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True, 'data': {'id': template.id}})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating template {id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to update template'}), 500

@app.route('/api/templates/<int:id>', methods=['DELETE'])
@login_required
def api_delete_template(id):
    """Delete a template via API."""
    try:
        template = CeremonyTemplate.query.filter_by(id=id, celebrant_id=current_user.id).first()
        if not template:
            return jsonify({'success': False, 'error': 'Template not found'}), 404
        
        db.session.delete(template)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting template {id}: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to delete template'}), 500

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
    from legal_forms_service import LegalFormsService
    app.register_blueprint(legal_forms_bp, url_prefix='/legal-forms')
    logger.info("Legal forms blueprint registered successfully")
    
    # Add context processor for legal forms alerts
    @app.context_processor
    def inject_legal_forms_alerts():
        """Inject legal forms alert count into all templates."""
        if current_user.is_authenticated:
            try:
                # Handle legacy users without organization_id
                if hasattr(current_user, 'organization_id') and current_user.organization_id:
                    service = LegalFormsService()
                    urgent_count = service.get_urgent_alerts_count(current_user.organization_id)
                    return {'urgent_alerts_count': urgent_count}
                else:
                    return {'urgent_alerts_count': 0}
            except Exception as e:
                logger.warning(f"Error getting urgent alerts count: {e}")
                return {'urgent_alerts_count': 0}
        return {'urgent_alerts_count': 0}
        
except ImportError as e:
    logger.warning(f"Could not register legal forms blueprint: {e}")
    
    # Provide default context processor if legal forms not available
    @app.context_processor
    def inject_default_alerts():
        return {'urgent_alerts_count': 0}

# Invoice Routes
try:
    from invoice_routes import invoice_bp
    app.register_blueprint(invoice_bp, url_prefix='/invoices')
    logger.info("Invoice blueprint registered successfully")
except ImportError as e:
    logger.warning(f"Could not register invoice blueprint: {e}")

# Google Maps Integration Routes
try:
    from services.maps_service import GoogleMapsService
    maps_service = GoogleMapsService()
    
    @app.route('/api/maps/calculate-distance', methods=['POST'])
    @login_required
    def calculate_distance():
        """Calculate distance and travel fee for a venue."""
        try:
            data = request.get_json()
            destination = data.get('destination', '').strip()
            
            if not destination:
                return jsonify({'success': False, 'error': 'Destination address required'}), 400
            
            # Basic address validation
            if len(destination) < 5:
                return jsonify({
                    'success': False, 
                    'error': 'Address too short. Please include street, suburb, and state.'
                }), 400
            
            # Get departure time if provided
            departure_time = None
            if data.get('departure_time'):
                departure_time = datetime.fromisoformat(data['departure_time'])
            
            result = maps_service.calculate_distance_and_time(destination, departure_time)
            
            if result:
                return jsonify({
                    'success': True,
                    'data': result,
                    'maps_url': maps_service.generate_maps_url(destination),
                    'embed_url': maps_service.generate_embed_map_url(destination)
                })
            else:
                # Provide more helpful error message
                error_msg = 'Address not found. Please check the spelling and include more details like street, suburb, and state (VIC).'
                return jsonify({'success': False, 'error': error_msg}), 400
                
        except Exception as e:
            logger.error(f"Error calculating distance: {str(e)}")
            return jsonify({'success': False, 'error': 'Unable to calculate distance. Please try again.'}), 500
    
    @app.route('/api/maps/update-couple-travel/<int:couple_id>', methods=['POST'])
    @login_required
    def update_couple_travel(couple_id):
        """Update travel information for a specific couple."""
        try:
            # Check if couple belongs to current user
            couple = Couple.query.get_or_404(couple_id)
            if couple.celebrant_id != current_user.id:
                return jsonify({'success': False, 'error': 'Access denied'}), 403
            
            result = maps_service.update_couple_travel_info(couple_id)
            
            if result['success']:
                return jsonify(result)
            else:
                return jsonify(result), 400
                
        except Exception as e:
            logger.error(f"Error updating couple travel info: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/maps/batch-calculate', methods=['POST'])
    @login_required
    def batch_calculate_distances():
        """Calculate distances for multiple couples."""
        try:
            # Get all couples for the current user with ceremony locations
            couples = Couple.query.filter_by(celebrant_id=current_user.id)\
                                 .filter(Couple.ceremony_location.isnot(None))\
                                 .all()
            
            if not couples:
                return jsonify({'success': True, 'message': 'No couples with ceremony locations found', 'results': {}})
            
            destinations = [couple.ceremony_location for couple in couples]
            results = maps_service.batch_calculate_distances(destinations)
            
            # Update couples with calculated travel fees
            updated_count = 0
            for couple in couples:
                if couple.ceremony_location in results:
                    result = results[couple.ceremony_location]
                    if 'travel_fee' in result:
                        couple.travel_fee = result['travel_fee']
                        updated_count += 1
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'results': results,
                'updated_couples': updated_count,
                'total_couples': len(couples)
            })
            
        except Exception as e:
            logger.error(f"Error in batch distance calculation: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/maps/venue-info', methods=['POST'])
    @login_required
    def get_venue_info():
        """Get comprehensive venue information including location and travel details."""
        try:
            data = request.get_json()
            venue_name = data.get('venue_name')
            address = data.get('address')
            
            if not venue_name:
                return jsonify({'success': False, 'error': 'Venue name required'}), 400
            
            # Use the maps service to get venue info (this would need to be implemented)
            # For now, we'll use the existing calculate_distance_and_time method
            search_query = venue_name
            if address:
                search_query += f", {address}"
            
            result = maps_service.calculate_distance_and_time(search_query)
            
            if result:
                return jsonify({
                    'success': True,
                    'venue_info': {
                        'name': venue_name,
                        'address': result['destination'],
                        'distance_km': result['distance_km'],
                        'travel_time': result['duration_text'],
                        'travel_fee': result['travel_fee'],
                        'maps_url': maps_service.generate_maps_url(search_query)
                    }
                })
            else:
                return jsonify({'success': False, 'error': 'Could not find venue information'}), 400
                
        except Exception as e:
            logger.error(f"Error getting venue info: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/api/maps/config', methods=['GET'])
    @login_required
    def maps_config():
        """Check if Google Maps is configured."""
        try:
            return jsonify({
                'success': True,
                'configured': bool(maps_service.api_key),
                'home_address': maps_service.home_address if maps_service.api_key else None
            })
        except Exception as e:
            logger.error(f"Error checking Maps config: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
    
    @app.route('/maps-travel')
    @login_required
    def maps_travel():
        """Maps and Travel management page."""
        return render_template('maps_travel.html', 
                             title='Maps & Travel Management',
                             maps_api_key=maps_service.api_key)
    
    logger.info("Google Maps integration routes registered successfully")
    
except ImportError as e:
    logger.warning(f"Could not register Google Maps routes: {e}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Only use debug mode in development
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    port = int(os.environ.get('PORT', 8085))
    app.run(host='0.0.0.0', port=port, debug=debug_mode) 