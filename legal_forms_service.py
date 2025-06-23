"""
Legal Forms Service - Handles form management, compliance tracking, and automated workflows
"""
import os
import json
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple
from flask import current_app, url_for
from werkzeug.utils import secure_filename
from models import (
    db, LegalFormSubmission, ComplianceAlert, ReminderLog,
    Couple, Organization, User
)


class LegalFormsService:
    """Service class for managing legal forms and compliance."""
    
    # Australian legal form requirements
    FORM_TYPES = {
        'noim': {
            'name': 'Notice of Intended Marriage',
            'description': 'Required at least 1 month before ceremony',
            'deadline_days': 31,
            'mandatory': True
        },
        'declaration': {
            'name': 'Declaration of No Impediment',
            'description': 'Required for some circumstances',
            'deadline_days': 7,
            'mandatory': False
        },
        'divorce_certificate': {
            'name': 'Divorce Certificate',
            'description': 'Required if previously married',
            'deadline_days': 14,
            'mandatory': False
        },
        'death_certificate': {
            'name': 'Death Certificate',
            'description': 'Required if widowed',
            'deadline_days': 14,
            'mandatory': False
        }
    }
    
    ALLOWED_FILE_TYPES = {'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @classmethod
    def initialize_couple_forms(cls, couple_id: int) -> Dict:
        """Initialize required legal forms for a new couple."""
        try:
            couple = Couple.query.get(couple_id)
            if not couple:
                return {'success': False, 'error': 'Couple not found'}
            
            if not couple.ceremony_date:
                return {'success': False, 'error': 'Ceremony date required'}
            
            forms_created = []
            
            # Always create NOIM form
            noim_form = cls._create_form_submission(
                couple=couple,
                form_type='noim'
            )
            if noim_form:
                forms_created.append(noim_form)
            
            # Create other forms based on couple's circumstances
            # This could be enhanced with a questionnaire system
            
            db.session.commit()
            
            return {
                'success': True,
                'forms_created': len(forms_created),
                'forms': [f.form_type for f in forms_created]
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def _create_form_submission(cls, couple: Couple, form_type: str) -> Optional[LegalFormSubmission]:
        """Create a new form submission record."""
        # Check if form already exists
        existing = LegalFormSubmission.query.filter_by(
            couple_id=couple.id,
            form_type=form_type
        ).first()
        
        if existing:
            return None
        
        form = LegalFormSubmission(
            organization_id=couple.organization_id,
            couple_id=couple.id,
            form_type=form_type,
            status='not_started'
        )
        
        # Calculate deadline
        form.calculate_deadline(couple.ceremony_date, form_type)
        
        # Generate reminder schedule
        form.generate_reminder_schedule()
        
        db.session.add(form)
        return form
    
    @classmethod
    def submit_form(cls, form_id: int, file_data: Dict, submitted_by: str) -> Dict:
        """Handle form submission with file upload."""
        try:
            form = LegalFormSubmission.query.get(form_id)
            if not form:
                return {'success': False, 'error': 'Form not found'}
            
            # Validate file
            validation_result = cls._validate_uploaded_file(file_data)
            if not validation_result['valid']:
                return {'success': False, 'error': validation_result['error']}
            
            # Save file
            file_path = cls._save_uploaded_file(file_data, form)
            if not file_path:
                return {'success': False, 'error': 'Failed to save file'}
            
            # Update form record
            form.status = 'completed'
            form.submitted_at = datetime.utcnow()
            form.submitted_by = submitted_by
            form.file_path = file_path
            form.file_type = file_data.get('content_type', '').split('/')[-1]
            form.file_size = file_data.get('size', 0)
            
            # Create validation alert for celebrant
            alert = ComplianceAlert(
                organization_id=form.organization_id,
                couple_id=form.couple_id,
                form_submission_id=form.id,
                alert_type='validation_required',
                severity='medium',
                title=f'{form.form_type.upper()} form submitted',
                message=f'{form.form_type.upper()} form submitted by {submitted_by} - requires validation'
            )
            db.session.add(alert)
            
            db.session.commit()
            
            return {
                'success': True,
                'form_id': form.id,
                'status': form.status,
                'file_path': file_path
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def validate_form(cls, form_id: int, validator_id: int, is_valid: bool, notes: str = '') -> Dict:
        """Validate a submitted form."""
        try:
            form = LegalFormSubmission.query.get(form_id)
            if not form:
                return {'success': False, 'error': 'Form not found'}
            
            form.is_validated = is_valid
            form.validated_by = validator_id
            form.validated_at = datetime.utcnow()
            form.validation_notes = notes
            
            if not is_valid:
                # Reset status if validation failed
                form.status = 'in_progress'
                
                # Create alert for couple to resubmit
                alert = ComplianceAlert(
                    organization_id=form.organization_id,
                    couple_id=form.couple_id,
                    form_submission_id=form.id,
                    alert_type='resubmission_required',
                    severity='high',
                    title=f'{form.form_type.upper()} form requires resubmission',
                    message=f'Form validation failed: {notes}'
                )
                db.session.add(alert)
            
            # Resolve validation alert
            validation_alert = ComplianceAlert.query.filter_by(
                form_submission_id=form.id,
                alert_type='validation_required',
                is_resolved=False
            ).first()
            
            if validation_alert:
                validation_alert.is_resolved = True
                validation_alert.resolved_at = datetime.utcnow()
                validation_alert.resolved_by = validator_id
            
            db.session.commit()
            
            return {
                'success': True,
                'form_id': form.id,
                'is_valid': is_valid,
                'status': form.status
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def get_compliance_dashboard(cls, organization_id: int) -> Dict:
        """Get compliance dashboard data for an organization."""
        try:
            # Get all forms for organization
            all_forms = LegalFormSubmission.query.filter_by(
                organization_id=organization_id
            ).all()
            
            # Calculate statistics
            total_forms = len(all_forms)
            completed_forms = len([f for f in all_forms if f.status == 'completed'])
            overdue_forms = len([f for f in all_forms if f.is_overdue])
            
            # Get upcoming deadlines (next 30 days)
            upcoming_deadline = date.today() + timedelta(days=30)
            upcoming_forms = [
                f for f in all_forms 
                if f.legal_deadline <= upcoming_deadline and f.status != 'completed'
            ]
            
            # Get active alerts
            active_alerts = ComplianceAlert.query.filter_by(
                organization_id=organization_id,
                is_resolved=False
            ).order_by(ComplianceAlert.severity.desc(), ComplianceAlert.created_at.desc()).all()
            
            # Group forms by couple
            couples_data = {}
            for form in all_forms:
                couple_id = form.couple_id
                if couple_id not in couples_data:
                    couples_data[couple_id] = {
                        'couple': form.couple,
                        'forms': [],
                        'compliance_score': 0,
                        'overdue_count': 0,
                        'upcoming_count': 0
                    }
                
                couples_data[couple_id]['forms'].append(form)
                if form.is_overdue:
                    couples_data[couple_id]['overdue_count'] += 1
                if form in upcoming_forms:
                    couples_data[couple_id]['upcoming_count'] += 1
            
            # Calculate compliance scores
            for couple_id, data in couples_data.items():
                data['compliance_score'] = data['couple'].compliance_score()
            
            return {
                'success': True,
                'statistics': {
                    'total_forms': total_forms,
                    'completed_forms': completed_forms,
                    'overdue_forms': overdue_forms,
                    'upcoming_forms': len(upcoming_forms),
                    'compliance_rate': (completed_forms / total_forms * 100) if total_forms > 0 else 100
                },
                'couples': list(couples_data.values()),
                'alerts': active_alerts,
                'upcoming_deadlines': upcoming_forms
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def get_couple_forms_status(cls, couple_id: int) -> Dict:
        """Get detailed forms status for a specific couple."""
        try:
            couple = Couple.query.get(couple_id)
            if not couple:
                return {'success': False, 'error': 'Couple not found'}
            
            forms = LegalFormSubmission.query.filter_by(couple_id=couple_id).all()
            
            forms_data = []
            for form in forms:
                form_info = cls.FORM_TYPES.get(form.form_type, {})
                forms_data.append({
                    'id': form.id,
                    'type': form.form_type,
                    'name': form_info.get('name', form.form_type.title()),
                    'description': form_info.get('description', ''),
                    'status': form.status,
                    'deadline': form.legal_deadline.isoformat() if form.legal_deadline else None,
                    'days_until_deadline': form.days_until_deadline,
                    'urgency_level': form.urgency_level,
                    'is_overdue': form.is_overdue,
                    'submitted_at': form.submitted_at.isoformat() if form.submitted_at else None,
                    'submitted_by': form.submitted_by,
                    'is_validated': form.is_validated,
                    'validation_notes': form.validation_notes
                })
            
            return {
                'success': True,
                'couple': {
                    'id': couple.id,
                    'names': couple.full_names,
                    'ceremony_date': couple.ceremony_date.isoformat() if couple.ceremony_date else None,
                    'compliance_score': couple.compliance_score()
                },
                'forms': forms_data
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def _validate_uploaded_file(cls, file_data: Dict) -> Dict:
        """Validate uploaded file."""
        if not file_data.get('filename'):
            return {'valid': False, 'error': 'No file provided'}
        
        filename = file_data['filename']
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        if file_ext not in cls.ALLOWED_FILE_TYPES:
            return {
                'valid': False, 
                'error': f'File type not allowed. Allowed types: {", ".join(cls.ALLOWED_FILE_TYPES)}'
            }
        
        file_size = file_data.get('size', 0)
        if file_size > cls.MAX_FILE_SIZE:
            return {
                'valid': False,
                'error': f'File too large. Maximum size: {cls.MAX_FILE_SIZE // (1024*1024)}MB'
            }
        
        return {'valid': True}
    
    @classmethod
    def _save_uploaded_file(cls, file_data: Dict, form: LegalFormSubmission) -> Optional[str]:
        """Save uploaded file to secure location."""
        try:
            filename = secure_filename(file_data['filename'])
            
            # Create directory structure: uploads/org_id/couple_id/form_type/
            upload_dir = os.path.join(
                current_app.config.get('UPLOAD_FOLDER', 'uploads'),
                str(form.organization_id),
                str(form.couple_id),
                form.form_type
            )
            
            os.makedirs(upload_dir, exist_ok=True)
            
            # Add timestamp to filename to avoid conflicts
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            name, ext = os.path.splitext(filename)
            unique_filename = f"{name}_{timestamp}{ext}"
            
            file_path = os.path.join(upload_dir, unique_filename)
            
            # Save file (this would need to be adapted based on your file handling)
            # For now, we'll just return the path
            return file_path
            
        except Exception as e:
            current_app.logger.error(f"Failed to save file: {str(e)}")
            return None
    
    @classmethod
    def send_reminder_email(cls, form_id: int, days_before_deadline: int) -> Dict:
        """Send reminder email for a specific form."""
        try:
            form = LegalFormSubmission.query.get(form_id)
            if not form:
                return {'success': False, 'error': 'Form not found'}
            
            couple = form.couple
            recipient_email = couple.primary_email
            
            if not recipient_email:
                return {'success': False, 'error': 'No email address found'}
            
            # Generate email content
            subject, content = cls._generate_reminder_email(form, days_before_deadline)
            
            # Send email (placeholder - integrate with actual email service)
            email_sent = cls._send_email(recipient_email, subject, content)
            
            # Log the reminder
            reminder_log = ReminderLog(
                organization_id=form.organization_id,
                couple_id=form.couple_id,
                form_submission_id=form.id,
                reminder_type='email',
                recipient=recipient_email,
                subject=subject,
                content=content,
                days_before_deadline=days_before_deadline,
                template_used='legal_form_reminder',
                delivery_status='sent' if email_sent else 'failed'
            )
            db.session.add(reminder_log)
            db.session.commit()
            
            return {
                'success': email_sent,
                'recipient': recipient_email,
                'days_before_deadline': days_before_deadline
            }
            
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def _generate_reminder_email(cls, form: LegalFormSubmission, days_before_deadline: int) -> Tuple[str, str]:
        """Generate reminder email subject and content."""
        urgency_text = {
            1: "URGENT - FINAL NOTICE",
            3: "URGENT",
            7: "Important",
            14: "Reminder",
            30: "Friendly Reminder"
        }.get(days_before_deadline, "Reminder")
        
        form_info = cls.FORM_TYPES.get(form.form_type, {})
        form_name = form_info.get('name', form.form_type.upper())
        
        subject = f"{urgency_text}: {form_name} Required - {days_before_deadline} Days Remaining"
        
        content = f"""
Dear {form.couple.partner1_name} and {form.couple.partner2_name},

{urgency_text}: Your {form_name} form is required in {days_before_deadline} days.

LEGAL REQUIREMENT:
This form is legally required for your marriage ceremony on {form.couple.ceremony_date.strftime('%B %d, %Y')}.

DEADLINE: {form.legal_deadline.strftime('%B %d, %Y')}

WHAT YOU NEED TO DO:
1. Complete the {form_name} form
2. Upload the signed document to your client portal
3. Ensure all required signatures and information are included

ACCESS YOUR PORTAL:
[Client Portal Link - To Be Configured]

IMPORTANT: Failure to submit this form by the deadline may result in your ceremony being postponed or cancelled.

If you have any questions or need assistance, please contact your celebrant immediately.

Best regards,
Your Celebrant Team

---
This is an automated reminder. Please do not reply to this email.
"""
        return subject, content
    
    @classmethod
    def _send_email(cls, to: str, subject: str, content: str) -> bool:
        """Send email (placeholder for actual email service integration)."""
        try:
            # Placeholder for email service integration
            # You would integrate with:
            # - SendGrid
            # - AWS SES
            # - Mailgun
            # - SMTP
            
            print(f"EMAIL SENT: {to} - {subject}")
            return True
            
        except Exception as e:
            print(f"Email sending failed: {str(e)}")
            return False
    
    @classmethod
    def generate_compliance_report(cls, organization_id: int) -> Dict:
        """Generate detailed compliance report."""
        try:
            dashboard_data = cls.get_compliance_dashboard(organization_id)
            if not dashboard_data['success']:
                return dashboard_data
            
            org = Organization.query.get(organization_id)
            stats = dashboard_data['statistics']
            
            report = {
                'organization': org.name,
                'generated_at': datetime.utcnow().isoformat(),
                'summary': stats,
                'couples_analysis': [],
                'recommendations': []
            }
            
            # Analyze each couple
            for couple_data in dashboard_data['couples']:
                couple = couple_data['couple']
                analysis = {
                    'couple_name': couple.full_names,
                    'ceremony_date': couple.ceremony_date.isoformat() if couple.ceremony_date else None,
                    'compliance_score': couple_data['compliance_score'],
                    'overdue_forms': couple_data['overdue_count'],
                    'upcoming_deadlines': couple_data['upcoming_count'],
                    'status': 'critical' if couple_data['overdue_count'] > 0 else 
                             'warning' if couple_data['upcoming_count'] > 0 else 'good'
                }
                report['couples_analysis'].append(analysis)
            
            # Generate recommendations
            if stats['overdue_forms'] > 0:
                report['recommendations'].append(
                    f"URGENT: {stats['overdue_forms']} forms are overdue and require immediate attention"
                )
            
            if stats['upcoming_forms'] > 0:
                report['recommendations'].append(
                    f"Follow up on {stats['upcoming_forms']} forms with upcoming deadlines"
                )
            
            if stats['compliance_rate'] < 80:
                report['recommendations'].append(
                    "Consider implementing additional reminder processes to improve compliance rate"
                )
            
            return {'success': True, 'report': report}
            
        except Exception as e:
            return {'success': False, 'error': str(e)} 