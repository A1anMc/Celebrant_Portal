"""
Database models for the Celebrant Portal with multi-tenancy support
"""
from datetime import datetime, date, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql.schema import Column, ForeignKey, Index
from sqlalchemy.sql.sqltypes import Integer, String, Text, Boolean, DateTime, Date, Float
from sqlalchemy.orm import relationship
import json

db = SQLAlchemy()


class Organization(db.Model):
    """Organization model for multi-tenancy."""
    __tablename__ = 'organizations'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)  # URL-friendly identifier
    domain = Column(String(100), unique=True, nullable=True)  # Custom domain
    subdomain = Column(String(50), unique=True, nullable=True)  # subdomain.celebrant.com
    
    # Contact Information
    contact_name = Column(String(100), nullable=True)
    contact_email = Column(String(120), nullable=True)
    contact_phone = Column(String(20), nullable=True)
    
    # Address
    address_line1 = Column(String(200), nullable=True)
    address_line2 = Column(String(200), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    postal_code = Column(String(20), nullable=True)
    country = Column(String(50), default='Australia', nullable=True)
    
    # Business Information
    abn = Column(String(20), nullable=True)  # Australian Business Number
    business_name = Column(String(200), nullable=True)
    website = Column(String(200), nullable=True)
    
    # Settings
    timezone = Column(String(50), default='Australia/Melbourne', nullable=True)
    currency = Column(String(3), default='AUD', nullable=True)
    date_format = Column(String(20), default='DD/MM/YYYY', nullable=True)
    
    # Subscription & Limits
    subscription_plan = Column(String(50), default='free', nullable=True)  # free, basic, premium
    max_users = Column(Integer, default=1, nullable=True)
    max_couples = Column(Integer, default=10, nullable=True)  # -1 for unlimited
    max_templates = Column(Integer, default=5, nullable=True)  # -1 for unlimited
    
    # Status
    is_active = Column(Boolean, default=True, nullable=True)
    is_trial = Column(Boolean, default=True, nullable=True)
    trial_ends_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add indexes for performance
    __table_args__ = (
        db.Index('idx_org_slug', 'slug'),
        db.Index('idx_org_domain', 'domain'),
        db.Index('idx_org_subdomain', 'subdomain'),
        db.Index('idx_org_active', 'is_active'),
    )
    
    # Relationships
    users = relationship('User', back_populates='organization', cascade='all, delete-orphan')
    couples = relationship('Couple', back_populates='organization', cascade='all, delete-orphan')
    templates = relationship('CeremonyTemplate', back_populates='organization', cascade='all, delete-orphan')
    legal_forms = relationship('LegalFormSubmission', back_populates='organization', cascade='all, delete-orphan')
    invoices = relationship('Invoice', back_populates='organization', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Organization {self.name}>'
    
    @property
    def is_over_user_limit(self):
        """Check if organization is over user limit."""
        if self.max_users == -1:  # Unlimited
            return False
        return len(self.users) >= self.max_users
    
    @property
    def is_over_couple_limit(self):
        """Check if organization is over couple limit."""
        if self.max_couples == -1:  # Unlimited
            return False
        return len(self.couples) >= self.max_couples
    
    @property
    def is_over_template_limit(self):
        """Check if organization is over template limit."""
        if self.max_templates == -1:  # Unlimited
            return False
        return len(self.templates) >= self.max_templates
    
    @property
    def usage_stats(self):
        """Get usage statistics for the organization."""
        return {
            'users': {
                'current': len(self.users),
                'limit': self.max_users,
                'percentage': (len(self.users) / self.max_users * 100) if self.max_users > 0 else 0
            },
            'couples': {
                'current': len(self.couples),
                'limit': self.max_couples,
                'percentage': (len(self.couples) / self.max_couples * 100) if self.max_couples > 0 else 0
            },
            'templates': {
                'current': len(self.templates),
                'limit': self.max_templates,
                'percentage': (len(self.templates) / self.max_templates * 100) if self.max_templates > 0 else 0
            }
        }


class User(UserMixin, db.Model):
    """User model for authentication with organization support."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(64), nullable=False)  # Removed unique constraint for multi-tenancy
    password_hash = Column(String(128), nullable=False)
    email = Column(String(120), nullable=False)  # Removed unique constraint for multi-tenancy
    name = Column(String(100), nullable=True)
    
    # Role and permissions
    role = Column(String(50), default='celebrant', nullable=True)  # owner, admin, celebrant, assistant
    is_admin = Column(Boolean, default=False, nullable=True)  # Organization admin
    is_active = Column(Boolean, default=True, nullable=True)
    
    # Multi-tenancy
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    
    # Metadata
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add composite unique constraints for multi-tenancy
    __table_args__ = (
        db.UniqueConstraint('email', 'organization_id', name='uq_user_email_org'),
        db.UniqueConstraint('username', 'organization_id', name='uq_user_username_org'),
        db.Index('idx_user_email_org', 'email', 'organization_id'),
        db.Index('idx_user_active', 'is_active'),
        db.Index('idx_user_role', 'role'),
    )
    
    # Relationships
    organization = relationship('Organization', back_populates='users')
    couples = relationship('Couple', back_populates='celebrant')
    templates = relationship('CeremonyTemplate', back_populates='celebrant')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @property
    def is_owner(self):
        """Check if user is organization owner."""
        return self.role == 'owner'
    
    @property
    def can_manage_users(self):
        """Check if user can manage other users."""
        return self.role in ['owner', 'admin']
    
    @property
    def can_manage_billing(self):
        """Check if user can manage billing."""
        return self.role == 'owner'


class Couple(db.Model):
    """Model for couples getting married with organization support."""
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
    
    # Multi-tenancy
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    
    # Foreign Keys
    celebrant_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    template_id = Column(Integer, ForeignKey('ceremony_templates.id'), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add indexes for performance
    __table_args__ = (
        db.Index('idx_couple_org', 'organization_id'),
        db.Index('idx_couple_names_org', 'partner1_name', 'partner2_name', 'organization_id'),
        db.Index('idx_couple_date_org', 'ceremony_date', 'organization_id'),
        db.Index('idx_couple_status_org', 'status', 'organization_id'),
        db.Index('idx_couple_celebrant', 'celebrant_id'),
    )
    
    # Relationships
    organization = relationship('Organization', back_populates='couples')
    celebrant = relationship('User', back_populates='couples')
    template = relationship('CeremonyTemplate', back_populates='couples')
    legal_forms = relationship('LegalFormSubmission', back_populates='couple', cascade='all, delete-orphan')
    invoices = relationship('Invoice', back_populates='couple', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Couple {self.partner1_name} & {self.partner2_name}>'
    
    @property
    def full_names(self):
        """Get full names of both partners."""
        return f"{self.partner1_name} & {self.partner2_name}"
    
    @property
    def primary_email(self):
        """Get primary email address."""
        return self.partner1_email or self.partner2_email

    def get_form_status(self, form_type):
        """Get status of a specific form type for this couple."""
        form = LegalFormSubmission.query.filter_by(
            couple_id=self.id,
            form_type=form_type
        ).first()
        return form.status if form else 'not_started'

    def get_overdue_forms(self):
        """Get all overdue forms for this couple."""
        return [form for form in self.legal_forms if form.is_overdue and form.status != 'completed']

    def get_upcoming_deadlines(self, days=30):
        """Get forms with deadlines in the next N days."""
        cutoff_date = date.today() + timedelta(days=days)
        return [
            form for form in self.legal_forms 
            if form.legal_deadline and form.legal_deadline <= cutoff_date and form.status != 'completed'
        ]

    def compliance_score(self):
        """Calculate compliance score (0-100) based on form completion."""
        if not self.legal_forms:
            return 0
        
        completed = sum(1 for form in self.legal_forms if form.status == 'completed')
        total = len(self.legal_forms)
        return int((completed / total) * 100) if total > 0 else 0


class CeremonyTemplate(db.Model):
    """Model for ceremony templates with organization support."""
    __tablename__ = 'ceremony_templates'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    ceremony_type = Column(String(50), nullable=True)
    is_default = Column(Boolean, default=False, nullable=True)
    is_shared = Column(Boolean, default=False, nullable=True)  # Shared across organizations
    
    # Multi-tenancy
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True)  # Null for shared templates
    celebrant_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add indexes for performance
    __table_args__ = (
        db.Index('idx_template_org', 'organization_id'),
        db.Index('idx_template_type_org', 'ceremony_type', 'organization_id'),
        db.Index('idx_template_name_org', 'name', 'organization_id'),
        db.Index('idx_template_shared', 'is_shared'),
        db.Index('idx_template_celebrant', 'celebrant_id'),
    )
    
    # Relationships
    organization = relationship('Organization', back_populates='templates')
    celebrant = relationship('User', back_populates='templates')
    couples = relationship('Couple', back_populates='template')
    
    def __repr__(self):
        return f'<CeremonyTemplate {self.name}>'


class ImportedName(db.Model):
    """Model for storing imported names to scan for with organization support."""
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
    
    # Multi-tenancy
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add indexes for performance
    __table_args__ = (
        db.Index('idx_imported_org', 'organization_id'),
        db.Index('idx_imported_names_org', 'partner1_name', 'partner2_name', 'organization_id'),
        db.Index('idx_imported_processed_org', 'is_processed', 'organization_id'),
    )
    
    # Relationships
    organization = relationship('Organization')
    
    def __repr__(self):
        return f'<ImportedName {self.partner1_name} & {self.partner2_name}>'
    
    @property
    def full_names(self):
        """Get full names of both partners."""
        return f"{self.partner1_name} & {self.partner2_name}"


class ImportSession(db.Model):
    """Model for tracking CSV import sessions with organization support."""
    __tablename__ = 'import_sessions'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    total_rows = Column(Integer, nullable=False)
    processed_rows = Column(Integer, default=0)
    chunk_size = Column(Integer, default=100)
    current_chunk = Column(Integer, default=0)
    status = Column(String(50), default='pending')  # pending, processing, paused, completed, failed
    error_count = Column(Integer, default=0)
    column_mapping = Column(Text, nullable=True)  # JSON string of column mappings
    errors = Column(Text, nullable=True)  # JSON string of errors
    
    # Multi-tenancy
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add indexes for performance
    __table_args__ = (
        db.Index('idx_import_session_org', 'organization_id'),
        db.Index('idx_import_session_user', 'user_id'),
        db.Index('idx_import_session_status', 'status'),
    )
    
    # Relationships
    organization = relationship('Organization')
    user = relationship('User')
    
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
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 


class LegalFormSubmission(db.Model):
    """Legal form submissions (NOIM, Declaration, etc.) with compliance tracking."""
    __tablename__ = 'legal_form_submissions'
    
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    couple_id = Column(Integer, ForeignKey('couples.id'), nullable=False)
    
    # Form details
    form_type = Column(String(50), nullable=False)  # 'noim', 'declaration', 'other'
    status = Column(String(20), nullable=False, default='not_started')  # not_started, in_progress, completed, overdue
    
    # Compliance tracking
    legal_deadline = Column(Date, nullable=False)  # When form must be completed by law
    reminder_schedule = Column(Text)  # JSON array of reminder dates
    
    # Submission details
    submitted_at = Column(DateTime)
    submitted_by = Column(String(100))  # Partner name who submitted
    file_path = Column(String(500))  # Path to uploaded file
    file_type = Column(String(50))  # pdf, jpg, png, etc.
    file_size = Column(Integer)  # File size in bytes
    
    # Validation
    is_validated = Column(Boolean, default=False)
    validated_by = Column(Integer, ForeignKey('users.id'))
    validated_at = Column(DateTime)
    validation_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship('Organization', back_populates='legal_forms')
    couple = relationship('Couple', back_populates='legal_forms')
    validator = relationship('User', foreign_keys=[validated_by])
    
    # Indexes
    __table_args__ = (
        Index('idx_legal_forms_org_status', 'organization_id', 'status'),
        Index('idx_legal_forms_deadline', 'legal_deadline'),
        Index('idx_legal_forms_couple_type', 'couple_id', 'form_type'),
    )
    
    def __repr__(self):
        return f'<LegalForm {self.form_type} for {self.couple.full_names} - {self.status}>'
    
    @property
    def days_until_deadline(self):
        """Calculate days until legal deadline."""
        if not self.legal_deadline:
            return None
        delta = self.legal_deadline - date.today()
        return delta.days
    
    @property
    def is_overdue(self):
        """Check if form is overdue."""
        return self.days_until_deadline is not None and self.days_until_deadline < 0
    
    @property
    def urgency_level(self):
        """Get urgency level based on days until deadline."""
        days = self.days_until_deadline
        if days is None:
            return 'unknown'
        elif days < 0:
            return 'overdue'
        elif days <= 7:
            return 'critical'
        elif days <= 14:
            return 'high'
        elif days <= 30:
            return 'medium'
        else:
            return 'low'
    
    def calculate_deadline(self, ceremony_date, form_type):
        """Calculate legal deadline based on ceremony date and form type."""
        if form_type == 'noim':
            # NOIM must be submitted at least 1 month before ceremony
            self.legal_deadline = ceremony_date - timedelta(days=31)
        elif form_type == 'declaration':
            # Declaration typically needed 1 week before ceremony
            self.legal_deadline = ceremony_date - timedelta(days=7)
        else:
            # Default to 2 weeks before
            self.legal_deadline = ceremony_date - timedelta(days=14)
    
    def generate_reminder_schedule(self):
        """Generate reminder schedule based on deadline."""
        if not self.legal_deadline:
            return []
        
        reminders = []
        deadline = self.legal_deadline
        
        # Add reminders at various intervals before deadline
        reminder_days = [30, 14, 7, 3, 1]  # Days before deadline
        
        for days in reminder_days:
            reminder_date = deadline - timedelta(days=days)
            if reminder_date >= date.today():
                reminders.append({
                    'date': reminder_date.isoformat(),
                    'days_before_deadline': days,
                    'sent': False
                })
        
        self.reminder_schedule = json.dumps(reminders)
        return reminders


class Invoice(db.Model):
    """Invoice model for payment tracking with organization support."""
    __tablename__ = 'invoices'
    
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    couple_id = Column(Integer, ForeignKey('couples.id'), nullable=False)
    
    # Invoice details
    invoice_number = Column(String(50), nullable=False, unique=True)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default='AUD', nullable=False)
    description = Column(Text, nullable=True)
    
    # Payment details
    due_date = Column(Date, nullable=False)
    status = Column(String(20), default='pending', nullable=False)  # pending, paid, overdue, cancelled
    paid_at = Column(DateTime, nullable=True)
    paid_amount = Column(Float, nullable=True)
    
    # Proof of payment
    proof_of_payment_path = Column(String(500), nullable=True)
    proof_of_payment_filename = Column(String(255), nullable=True)
    proof_of_payment_uploaded_at = Column(DateTime, nullable=True)
    proof_of_payment_verified = Column(Boolean, default=False, nullable=False)
    proof_of_payment_verified_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    proof_of_payment_verified_at = Column(DateTime, nullable=True)
    
    # Payment method
    payment_method = Column(String(50), nullable=True)  # bank_transfer, cash, card, etc.
    transaction_reference = Column(String(100), nullable=True)
    
    # Reminders
    reminder_sent_7_days = Column(Boolean, default=False, nullable=False)
    reminder_sent_1_day = Column(Boolean, default=False, nullable=False)
    reminder_sent_overdue = Column(Boolean, default=False, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship('Organization')
    couple = relationship('Couple')
    verified_by = relationship('User', foreign_keys=[proof_of_payment_verified_by])
    
    # Indexes
    __table_args__ = (
        db.Index('idx_invoice_org', 'organization_id'),
        db.Index('idx_invoice_couple', 'couple_id'),
        db.Index('idx_invoice_status', 'status'),
        db.Index('idx_invoice_due_date', 'due_date'),
        db.Index('idx_invoice_number', 'invoice_number'),
    )
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'
    
    @property
    def is_overdue(self):
        """Check if invoice is overdue."""
        if self.status == 'paid':
            return False
        return self.due_date < date.today()
    
    @property
    def days_until_due(self):
        """Get days until due date (negative if overdue)."""
        if self.status == 'paid':
            return 0
        return (self.due_date - date.today()).days
    
    @property
    def urgency_level(self):
        """Get urgency level for reminders."""
        if self.status == 'paid':
            return 'none'
        
        days_until = self.days_until_due
        
        if days_until < 0:
            return 'critical'  # Overdue
        elif days_until <= 1:
            return 'high'  # Due today or tomorrow
        elif days_until <= 7:
            return 'medium'  # Due within a week
        else:
            return 'low'  # Due later
    
    @property
    def formatted_amount(self):
        """Get formatted amount with currency."""
        return f"{self.currency} {self.amount:.2f}"
    
    def generate_invoice_number(self):
        """Generate a unique invoice number."""
        if not self.invoice_number:
            # Format: INV-YYYYMMDD-XXXX
            today = datetime.now().strftime('%Y%m%d')
            # Get count of invoices for today
            count = Invoice.query.filter(
                Invoice.organization_id == self.organization_id,
                Invoice.created_at >= datetime.now().date()
            ).count() + 1
            self.invoice_number = f"INV-{today}-{count:04d}"
        return self.invoice_number
    
    def mark_as_paid(self, paid_amount=None, verified_by=None):
        """Mark invoice as paid."""
        self.status = 'paid'
        self.paid_at = datetime.utcnow()
        self.paid_amount = paid_amount or self.amount
        if verified_by:
            self.proof_of_payment_verified = True
            self.proof_of_payment_verified_by = verified_by
            self.proof_of_payment_verified_at = datetime.utcnow()
    
    def needs_reminder(self, days_before):
        """Check if reminder needs to be sent."""
        if self.status == 'paid':
            return False
        
        days_until = self.days_until_due
        
        if days_before == 7:
            return days_until == 7 and not self.reminder_sent_7_days
        elif days_before == 1:
            return days_until == 1 and not self.reminder_sent_1_day
        elif days_before == 0:  # Overdue
            return days_until < 0 and not self.reminder_sent_overdue
        
        return False
    
    def mark_reminder_sent(self, days_before):
        """Mark reminder as sent."""
        if days_before == 7:
            self.reminder_sent_7_days = True
        elif days_before == 1:
            self.reminder_sent_1_day = True
        elif days_before == 0:  # Overdue
            self.reminder_sent_overdue = True


class ComplianceAlert(db.Model):
    """Compliance alerts and notifications for celebrants."""
    __tablename__ = 'compliance_alerts'
    
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    couple_id = Column(Integer, ForeignKey('couples.id'), nullable=False)
    form_submission_id = Column(Integer, ForeignKey('legal_form_submissions.id'), nullable=True)
    
    # Alert details
    alert_type = Column(String(50), nullable=False)  # 'form_overdue', 'deadline_approaching', 'validation_required'
    severity = Column(String(20), nullable=False)  # 'low', 'medium', 'high', 'critical'
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Status
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    resolved_by = Column(Integer, ForeignKey('users.id'))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    organization = relationship('Organization')
    couple = relationship('Couple')
    form_submission = relationship('LegalFormSubmission')
    resolver = relationship('User', foreign_keys=[resolved_by])
    
    # Indexes
    __table_args__ = (
        Index('idx_alerts_org_resolved', 'organization_id', 'is_resolved'),
        Index('idx_alerts_severity', 'severity'),
    )


class ReminderLog(db.Model):
    """Log of sent reminders for tracking and audit purposes."""
    __tablename__ = 'reminder_logs'
    
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=False)
    couple_id = Column(Integer, ForeignKey('couples.id'), nullable=False)
    form_submission_id = Column(Integer, ForeignKey('legal_form_submissions.id'), nullable=False)
    
    # Reminder details
    reminder_type = Column(String(50), nullable=False)  # 'email', 'sms', 'in_app'
    recipient = Column(String(200), nullable=False)  # Email or phone number
    subject = Column(String(500))
    content = Column(Text)
    
    # Status
    sent_at = Column(DateTime, default=datetime.utcnow)
    delivery_status = Column(String(50), default='pending')  # pending, sent, delivered, failed
    error_message = Column(Text)
    
    # Metadata
    days_before_deadline = Column(Integer)
    template_used = Column(String(100))
    
    # Relationships
    organization = relationship('Organization')
    couple = relationship('Couple')
    form_submission = relationship('LegalFormSubmission')
    
    # Indexes
    __table_args__ = (
        Index('idx_reminders_org_sent', 'organization_id', 'sent_at'),
        Index('idx_reminders_status', 'delivery_status'),
    ) 