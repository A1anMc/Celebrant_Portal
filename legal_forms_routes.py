"""
Flask routes for legal forms management and compliance tracking
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from datetime import datetime, date

from legal_forms_service import LegalFormsService
from models import db, LegalFormSubmission, ComplianceAlert, Couple
from forms import LegalFormUploadForm, FormValidationForm

# Create blueprint
legal_forms_bp = Blueprint('legal_forms', __name__, url_prefix='/legal-forms')


@legal_forms_bp.route('/dashboard')
@login_required
def compliance_dashboard():
    """Compliance dashboard for celebrants."""
    if not current_user.organization_id:
        flash('Organization access required', 'error')
        return redirect(url_for('index'))
    
    dashboard_data = LegalFormsService.get_compliance_dashboard(current_user.organization_id)
    
    if not dashboard_data['success']:
        flash(f'Error loading dashboard: {dashboard_data["error"]}', 'error')
        return redirect(url_for('index'))
    
    return render_template('legal_forms/dashboard.html', 
                         data=dashboard_data,
                         title='Legal Forms Compliance Dashboard')


@legal_forms_bp.route('/couple/<int:couple_id>')
@login_required
def couple_forms_status(couple_id):
    """View legal forms status for a specific couple."""
    couple = Couple.query.get_or_404(couple_id)
    
    # Check organization access
    if couple.organization_id != current_user.organization_id:
        flash('Access denied', 'error')
        return redirect(url_for('legal_forms.compliance_dashboard'))
    
    forms_data = LegalFormsService.get_couple_forms_status(couple_id)
    
    if not forms_data['success']:
        flash(f'Error loading forms: {forms_data["error"]}', 'error')
        return redirect(url_for('legal_forms.compliance_dashboard'))
    
    return render_template('legal_forms/couple_forms.html',
                         data=forms_data,
                         couple=couple,
                         title=f'Legal Forms - {couple.full_names}')


@legal_forms_bp.route('/initialize/<int:couple_id>', methods=['POST'])
@login_required
def initialize_couple_forms(couple_id):
    """Initialize legal forms for a couple."""
    couple = Couple.query.get_or_404(couple_id)
    
    # Check organization access
    if couple.organization_id != current_user.organization_id:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    result = LegalFormsService.initialize_couple_forms(couple_id)
    
    if result['success']:
        flash(f'Initialized {result["forms_created"]} legal forms for {couple.full_names}', 'success')
    else:
        flash(f'Error initializing forms: {result["error"]}', 'error')
    
    return jsonify(result)


@legal_forms_bp.route('/upload/<int:form_id>', methods=['GET', 'POST'])
def upload_form(form_id):
    """Upload form submission (accessible by couples via secure link)."""
    form_submission = LegalFormSubmission.query.get_or_404(form_id)
    form = LegalFormUploadForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        file = form.file.data
        submitted_by = form.submitted_by.data
        
        if file and file.filename:
            # Prepare file data
            file_data = {
                'filename': secure_filename(file.filename),
                'content_type': file.content_type,
                'size': len(file.read())
            }
            file.seek(0)  # Reset file pointer
            
            # Save file temporarily and get path
            temp_path = os.path.join(current_app.config.get('UPLOAD_FOLDER', 'uploads'), 'temp')
            os.makedirs(temp_path, exist_ok=True)
            temp_file_path = os.path.join(temp_path, file_data['filename'])
            file.save(temp_file_path)
            file_data['temp_path'] = temp_file_path
            
            # Submit form
            result = LegalFormsService.submit_form(form_id, file_data, submitted_by)
            
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            
            if result['success']:
                flash('Form submitted successfully! Your celebrant will review it shortly.', 'success')
                return render_template('legal_forms/upload_success.html',
                                     form_submission=form_submission)
            else:
                flash(f'Error submitting form: {result["error"]}', 'error')
    
    return render_template('legal_forms/upload_form.html',
                         form=form,
                         form_submission=form_submission,
                         title=f'Upload {form_submission.form_type.upper()} Form')


@legal_forms_bp.route('/validate/<int:form_id>', methods=['GET', 'POST'])
@login_required
def validate_form(form_id):
    """Validate a submitted form."""
    form_submission = LegalFormSubmission.query.get_or_404(form_id)
    
    # Check organization access
    if form_submission.organization_id != current_user.organization_id:
        flash('Access denied', 'error')
        return redirect(url_for('legal_forms.compliance_dashboard'))
    
    form = FormValidationForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        is_valid = form.is_valid.data
        notes = form.validation_notes.data
        
        result = LegalFormsService.validate_form(form_id, current_user.id, is_valid, notes)
        
        if result['success']:
            status_text = 'approved' if is_valid else 'rejected'
            flash(f'Form {status_text} successfully', 'success')
            return redirect(url_for('legal_forms.compliance_dashboard'))
        else:
            flash(f'Error validating form: {result["error"]}', 'error')
    
    return render_template('legal_forms/validate_form.html',
                         form=form,
                         form_submission=form_submission,
                         title=f'Validate {form_submission.form_type.upper()} Form')


@legal_forms_bp.route('/send-reminder/<int:form_id>', methods=['POST'])
@login_required
def send_manual_reminder(form_id):
    """Send manual reminder for a form."""
    form_submission = LegalFormSubmission.query.get_or_404(form_id)
    
    # Check organization access
    if form_submission.organization_id != current_user.organization_id:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    days_before_deadline = form_submission.days_until_deadline or 0
    result = LegalFormsService.send_reminder_email(form_id, days_before_deadline)
    
    if result['success']:
        flash('Reminder sent successfully', 'success')
    else:
        flash(f'Error sending reminder: {result["error"]}', 'error')
    
    return jsonify(result)


@legal_forms_bp.route('/resolve-alert/<int:alert_id>', methods=['POST'])
@login_required
def resolve_alert(alert_id):
    """Resolve a compliance alert."""
    alert = ComplianceAlert.query.get_or_404(alert_id)
    
    # Check organization access
    if alert.organization_id != current_user.organization_id:
        return jsonify({'success': False, 'error': 'Access denied'}), 403
    
    try:
        alert.is_resolved = True
        alert.resolved_at = datetime.utcnow()
        alert.resolved_by = current_user.id
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Alert resolved'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@legal_forms_bp.route('/api/dashboard-stats')
@login_required
def api_dashboard_stats():
    """API endpoint for dashboard statistics."""
    if not current_user.organization_id:
        return jsonify({'error': 'Organization access required'}), 403
    
    dashboard_data = LegalFormsService.get_compliance_dashboard(current_user.organization_id)
    
    if dashboard_data['success']:
        return jsonify(dashboard_data['statistics'])
    else:
        return jsonify({'error': dashboard_data['error']}), 500


@legal_forms_bp.route('/api/upcoming-deadlines')
@login_required
def api_upcoming_deadlines():
    """API endpoint for upcoming deadlines."""
    if not current_user.organization_id:
        return jsonify({'error': 'Organization access required'}), 403
    
    dashboard_data = LegalFormsService.get_compliance_dashboard(current_user.organization_id)
    
    if dashboard_data['success']:
        deadlines = []
        for form in dashboard_data['upcoming_deadlines']:
            deadlines.append({
                'couple_name': form.couple.full_names,
                'form_type': form.form_type,
                'deadline': form.legal_deadline.isoformat(),
                'days_remaining': form.days_until_deadline,
                'urgency': form.urgency_level,
                'status': form.status
            })
        return jsonify(deadlines)
    else:
        return jsonify({'error': dashboard_data['error']}), 500


@legal_forms_bp.route('/report/compliance')
@login_required
def compliance_report():
    """Generate and display compliance report."""
    if not current_user.organization_id:
        flash('Organization access required', 'error')
        return redirect(url_for('index'))
    
    report_data = LegalFormsService.generate_compliance_report(current_user.organization_id)
    
    if not report_data['success']:
        flash(f'Error generating report: {report_data["error"]}', 'error')
        return redirect(url_for('legal_forms.compliance_dashboard'))
    
    return render_template('legal_forms/compliance_report.html',
                         report=report_data['report'],
                         title='Compliance Report')


@legal_forms_bp.route('/api/forms-by-status')
@login_required
def api_forms_by_status():
    """API endpoint for forms grouped by status."""
    if not current_user.organization_id:
        return jsonify({'error': 'Organization access required'}), 403
    
    try:
        forms = LegalFormSubmission.query.filter_by(
            organization_id=current_user.organization_id
        ).all()
        
        status_counts = {}
        for form in forms:
            status = form.status
            if status not in status_counts:
                status_counts[status] = 0
            status_counts[status] += 1
        
        return jsonify(status_counts)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@legal_forms_bp.route('/download/<int:form_id>')
@login_required
def download_form(form_id):
    """Download submitted form file."""
    form_submission = LegalFormSubmission.query.get_or_404(form_id)
    
    # Check organization access
    if form_submission.organization_id != current_user.organization_id:
        flash('Access denied', 'error')
        return redirect(url_for('legal_forms.compliance_dashboard'))
    
    if not form_submission.file_path or not os.path.exists(form_submission.file_path):
        flash('File not found', 'error')
        return redirect(url_for('legal_forms.compliance_dashboard'))
    
    return send_file(
        form_submission.file_path,
        as_attachment=True,
        download_name=f"{form_submission.form_type}_{form_submission.couple.full_names.replace(' ', '_')}.{form_submission.file_type}"
    )


# Error handlers for the blueprint
@legal_forms_bp.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@legal_forms_bp.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403


@legal_forms_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500


# Context processor to add common data to all templates
@legal_forms_bp.context_processor
def inject_legal_forms_data():
    """Inject common legal forms data into templates."""
    if current_user.is_authenticated and current_user.organization_id:
        # Get quick stats for sidebar/navigation
        try:
            dashboard_data = LegalFormsService.get_compliance_dashboard(current_user.organization_id)
            if dashboard_data['success']:
                return {
                    'legal_forms_stats': dashboard_data['statistics'],
                    'urgent_alerts_count': len([
                        alert for alert in dashboard_data['alerts'] 
                        if alert.severity in ['critical', 'high'] and not alert.is_resolved
                    ])
                }
        except:
            pass
    
    return {
        'legal_forms_stats': None,
        'urgent_alerts_count': 0
    } 