"""
Celery tasks for automated legal form reminders and compliance monitoring
"""
import os
import json
from datetime import datetime, date, timedelta
from celery import Celery
from flask import current_app
from sqlalchemy import and_

# Import models (will need to be adjusted based on app structure)
from models import (
    db, LegalFormSubmission, ComplianceAlert, ReminderLog, 
    Couple, Organization, User
)

# Configure Celery
def make_celery(app):
    """Create Celery instance and configure it with Flask app."""
    celery = Celery(
        app.import_name,
        backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        broker=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    )
    
    celery.conf.update(app.config)
    
    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery

# Initialize Celery (will be properly configured when integrated with main app)
celery = Celery('legal_forms')

# Configure Celery beat schedule for periodic tasks
celery.conf.beat_schedule = {
    'check-form-deadlines': {
        'task': 'celery_tasks.check_form_deadlines',
        'schedule': 3600.0,  # Run every hour
    },
    'send-daily-reminders': {
        'task': 'celery_tasks.send_daily_reminders',
        'schedule': 86400.0,  # Run daily at midnight
    },
    'generate-compliance-report': {
        'task': 'celery_tasks.generate_compliance_report',
        'schedule': 604800.0,  # Run weekly
    },
    'cleanup-old-alerts': {
        'task': 'celery_tasks.cleanup_old_alerts',
        'schedule': 86400.0,  # Run daily
    },
}

celery.conf.timezone = 'Australia/Melbourne'


@celery.task(bind=True, retry_backoff=True, max_retries=3)
def check_form_deadlines(self):
    """
    Check all legal form deadlines and create alerts for overdue/approaching deadlines.
    Runs hourly to ensure timely notifications.
    """
    try:
        current_time = datetime.utcnow()
        today = date.today()
        
        # Find forms approaching deadlines (next 7 days)
        approaching_deadline = today + timedelta(days=7)
        approaching_forms = LegalFormSubmission.query.filter(
            and_(
                LegalFormSubmission.status.in_(['not_started', 'in_progress']),
                LegalFormSubmission.legal_deadline <= approaching_deadline,
                LegalFormSubmission.legal_deadline >= today
            )
        ).all()
        
        # Find overdue forms
        overdue_forms = LegalFormSubmission.query.filter(
            and_(
                LegalFormSubmission.status.in_(['not_started', 'in_progress']),
                LegalFormSubmission.legal_deadline < today
            )
        ).all()
        
        alerts_created = 0
        
        # Create alerts for approaching deadlines
        for form in approaching_forms:
            # Check if alert already exists
            existing_alert = ComplianceAlert.query.filter(
                and_(
                    ComplianceAlert.form_submission_id == form.id,
                    ComplianceAlert.alert_type == 'deadline_approaching',
                    ComplianceAlert.is_resolved == False
                )
            ).first()
            
            if not existing_alert:
                days_remaining = form.days_until_deadline
                severity = 'critical' if days_remaining <= 3 else 'high'
                
                alert = ComplianceAlert(
                    organization_id=form.organization_id,
                    couple_id=form.couple_id,
                    form_submission_id=form.id,
                    alert_type='deadline_approaching',
                    severity=severity,
                    title=f'{form.form_type.upper()} deadline approaching',
                    message=f'{form.form_type.upper()} form for {form.couple.full_names} is due in {days_remaining} days'
                )
                db.session.add(alert)
                alerts_created += 1
        
        # Create alerts for overdue forms
        for form in overdue_forms:
            # Update form status to overdue
            if form.status != 'overdue':
                form.status = 'overdue'
            
            # Check if alert already exists
            existing_alert = ComplianceAlert.query.filter(
                and_(
                    ComplianceAlert.form_submission_id == form.id,
                    ComplianceAlert.alert_type == 'form_overdue',
                    ComplianceAlert.is_resolved == False
                )
            ).first()
            
            if not existing_alert:
                days_overdue = abs(form.days_until_deadline)
                
                alert = ComplianceAlert(
                    organization_id=form.organization_id,
                    couple_id=form.couple_id,
                    form_submission_id=form.id,
                    alert_type='form_overdue',
                    severity='critical',
                    title=f'{form.form_type.upper()} form overdue',
                    message=f'{form.form_type.upper()} form for {form.couple.full_names} is {days_overdue} days overdue'
                )
                db.session.add(alert)
                alerts_created += 1
        
        db.session.commit()
        
        return {
            'status': 'success',
            'alerts_created': alerts_created,
            'approaching_deadlines': len(approaching_forms),
            'overdue_forms': len(overdue_forms),
            'checked_at': current_time.isoformat()
        }
        
    except Exception as exc:
        db.session.rollback()
        self.retry(countdown=60, exc=exc)


@celery.task(bind=True, retry_backoff=True, max_retries=3)
def send_daily_reminders(self):
    """
    Send daily email/SMS reminders to couples with upcoming form deadlines.
    Runs daily to ensure couples receive timely reminders.
    """
    try:
        today = date.today()
        reminders_sent = 0
        
        # Get all forms that need reminders today
        forms_needing_reminders = LegalFormSubmission.query.filter(
            and_(
                LegalFormSubmission.status.in_(['not_started', 'in_progress']),
                LegalFormSubmission.reminder_schedule.isnot(None)
            )
        ).all()
        
        for form in forms_needing_reminders:
            if not form.reminder_schedule:
                continue
                
            try:
                schedule = json.loads(form.reminder_schedule)
            except (json.JSONDecodeError, TypeError):
                continue
            
            # Check if any reminders are due today
            for reminder in schedule:
                reminder_date = datetime.fromisoformat(reminder['date']).date()
                
                if reminder_date == today and not reminder.get('sent', False):
                    # Send reminder
                    success = send_form_reminder.delay(
                        form.id, 
                        reminder['days_before_deadline']
                    )
                    
                    if success:
                        # Mark reminder as sent
                        reminder['sent'] = True
                        form.reminder_schedule = json.dumps(schedule)
                        reminders_sent += 1
        
        db.session.commit()
        
        return {
            'status': 'success',
            'reminders_sent': reminders_sent,
            'checked_at': datetime.utcnow().isoformat()
        }
        
    except Exception as exc:
        db.session.rollback()
        self.retry(countdown=300, exc=exc)


@celery.task(bind=True, retry_backoff=True, max_retries=3)
def send_form_reminder(self, form_id, days_before_deadline):
    """
    Send a specific form reminder to a couple.
    """
    try:
        form = LegalFormSubmission.query.get(form_id)
        if not form or not form.couple:
            return {'status': 'error', 'message': 'Form or couple not found'}
        
        couple = form.couple
        
        # Determine recipient (prefer primary email)
        recipient_email = couple.primary_email
        if not recipient_email:
            return {'status': 'error', 'message': 'No email address found for couple'}
        
        # Generate reminder content
        subject = f"URGENT: {form.form_type.upper()} Form Required - {days_before_deadline} Days Remaining"
        
        content = generate_reminder_email_content(form, days_before_deadline)
        
        # Send email (integrate with your email service)
        email_sent = send_email_notification(
            to=recipient_email,
            subject=subject,
            content=content,
            form=form
        )
        
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
            'status': 'success' if email_sent else 'failed',
            'form_id': form_id,
            'recipient': recipient_email,
            'days_before_deadline': days_before_deadline
        }
        
    except Exception as exc:
        db.session.rollback()
        self.retry(countdown=300, exc=exc)


@celery.task
def generate_compliance_report(organization_id=None):
    """
    Generate weekly compliance reports for celebrants.
    """
    try:
        # Get organizations to report on
        if organization_id:
            organizations = [Organization.query.get(organization_id)]
        else:
            organizations = Organization.query.filter_by(is_active=True).all()
        
        reports = []
        
        for org in organizations:
            if not org:
                continue
                
            # Get compliance statistics
            total_forms = LegalFormSubmission.query.filter_by(organization_id=org.id).count()
            completed_forms = LegalFormSubmission.query.filter_by(
                organization_id=org.id, 
                status='completed'
            ).count()
            overdue_forms = LegalFormSubmission.query.filter(
                and_(
                    LegalFormSubmission.organization_id == org.id,
                    LegalFormSubmission.status == 'overdue'
                )
            ).count()
            
            # Get upcoming deadlines (next 30 days)
            upcoming_deadline = date.today() + timedelta(days=30)
            upcoming_forms = LegalFormSubmission.query.filter(
                and_(
                    LegalFormSubmission.organization_id == org.id,
                    LegalFormSubmission.status.in_(['not_started', 'in_progress']),
                    LegalFormSubmission.legal_deadline <= upcoming_deadline
                )
            ).count()
            
            compliance_rate = (completed_forms / total_forms * 100) if total_forms > 0 else 100
            
            report = {
                'organization': org.name,
                'total_forms': total_forms,
                'completed_forms': completed_forms,
                'overdue_forms': overdue_forms,
                'upcoming_forms': upcoming_forms,
                'compliance_rate': round(compliance_rate, 2),
                'generated_at': datetime.utcnow().isoformat()
            }
            reports.append(report)
            
            # Send report to organization admins
            send_compliance_report_email.delay(org.id, report)
        
        return {
            'status': 'success',
            'reports_generated': len(reports),
            'reports': reports
        }
        
    except Exception as exc:
        return {'status': 'error', 'message': str(exc)}


@celery.task
def send_compliance_report_email(organization_id, report_data):
    """
    Send compliance report email to organization administrators.
    """
    try:
        org = Organization.query.get(organization_id)
        if not org:
            return {'status': 'error', 'message': 'Organization not found'}
        
        # Get admin users for this organization
        admin_users = User.query.filter(
            and_(
                User.organization_id == organization_id,
                User.role.in_(['owner', 'admin'])
            )
        ).all()
        
        if not admin_users:
            return {'status': 'warning', 'message': 'No admin users found'}
        
        subject = f"Weekly Compliance Report - {org.name}"
        content = generate_compliance_report_email(report_data)
        
        emails_sent = 0
        for admin in admin_users:
            if admin.email:
                success = send_email_notification(
                    to=admin.email,
                    subject=subject,
                    content=content,
                    template='compliance_report'
                )
                if success:
                    emails_sent += 1
        
        return {
            'status': 'success',
            'organization': org.name,
            'emails_sent': emails_sent
        }
        
    except Exception as exc:
        return {'status': 'error', 'message': str(exc)}


@celery.task
def cleanup_old_alerts():
    """
    Clean up resolved alerts older than 30 days.
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        old_alerts = ComplianceAlert.query.filter(
            and_(
                ComplianceAlert.is_resolved == True,
                ComplianceAlert.resolved_at < cutoff_date
            )
        ).all()
        
        deleted_count = len(old_alerts)
        
        for alert in old_alerts:
            db.session.delete(alert)
        
        db.session.commit()
        
        return {
            'status': 'success',
            'deleted_alerts': deleted_count,
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as exc:
        db.session.rollback()
        return {'status': 'error', 'message': str(exc)}


@celery.task
def initialize_forms_for_couple(couple_id):
    """
    Initialize required legal forms when a new couple is created.
    """
    try:
        couple = Couple.query.get(couple_id)
        if not couple or not couple.ceremony_date:
            return {'status': 'error', 'message': 'Couple or ceremony date not found'}
        
        # Define required forms for Australian marriages
        required_forms = [
            {'type': 'noim', 'name': 'Notice of Intended Marriage'},
            {'type': 'declaration', 'name': 'Declaration of No Impediment'}
        ]
        
        forms_created = 0
        
        for form_info in required_forms:
            # Check if form already exists
            existing_form = LegalFormSubmission.query.filter_by(
                couple_id=couple_id,
                form_type=form_info['type']
            ).first()
            
            if not existing_form:
                form = LegalFormSubmission(
                    organization_id=couple.organization_id,
                    couple_id=couple_id,
                    form_type=form_info['type'],
                    status='not_started'
                )
                
                # Calculate deadline based on ceremony date
                form.calculate_deadline(couple.ceremony_date, form_info['type'])
                
                # Generate reminder schedule
                form.generate_reminder_schedule()
                
                db.session.add(form)
                forms_created += 1
        
        db.session.commit()
        
        return {
            'status': 'success',
            'couple_id': couple_id,
            'forms_created': forms_created
        }
        
    except Exception as exc:
        db.session.rollback()
        return {'status': 'error', 'message': str(exc)}


# Helper functions for email content generation

def generate_reminder_email_content(form, days_before_deadline):
    """Generate email content for form reminders."""
    urgency_text = {
        1: "URGENT - FINAL NOTICE",
        3: "URGENT",
        7: "Important",
        14: "Reminder",
        30: "Friendly Reminder"
    }.get(days_before_deadline, "Reminder")
    
    form_descriptions = {
        'noim': 'Notice of Intended Marriage (NOIM)',
        'declaration': 'Declaration of No Impediment'
    }
    
    form_name = form_descriptions.get(form.form_type, form.form_type.upper())
    
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
[Portal Link - to be configured]

IMPORTANT: Failure to submit this form by the deadline may result in your ceremony being postponed or cancelled.

If you have any questions or need assistance, please contact your celebrant immediately.

Best regards,
Your Celebrant Team

---
This is an automated reminder. Please do not reply to this email.
"""
    return content


def generate_compliance_report_email(report_data):
    """Generate email content for compliance reports."""
    content = f"""
Weekly Compliance Report - {report_data['organization']}

SUMMARY:
• Total Forms: {report_data['total_forms']}
• Completed: {report_data['completed_forms']}
• Overdue: {report_data['overdue_forms']}
• Upcoming Deadlines (30 days): {report_data['upcoming_forms']}
• Compliance Rate: {report_data['compliance_rate']}%

"""
    
    if report_data['overdue_forms'] > 0:
        content += f"""
⚠️  URGENT ACTION REQUIRED:
{report_data['overdue_forms']} forms are overdue and require immediate attention.
"""
    
    if report_data['upcoming_forms'] > 0:
        content += f"""
📅 UPCOMING DEADLINES:
{report_data['upcoming_forms']} forms have deadlines in the next 30 days.
"""
    
    content += """

Please log into your dashboard to review and take action on any pending forms.

Generated: """ + report_data['generated_at'] + """

---
This is an automated report.
"""
    return content


def send_email_notification(to, subject, content, template=None, form=None):
    """
    Send email notification (integrate with your email service).
    This is a placeholder - implement with your actual email service.
    """
    try:
        # Placeholder for email integration
        # You would integrate with services like:
        # - SendGrid
        # - AWS SES
        # - Mailgun
        # - SMTP
        
        print(f"EMAIL: {to} - {subject}")
        print(f"CONTENT: {content[:100]}...")
        
        # For now, return True to simulate successful sending
        return True
        
    except Exception as e:
        print(f"Email sending failed: {str(e)}")
        return False 