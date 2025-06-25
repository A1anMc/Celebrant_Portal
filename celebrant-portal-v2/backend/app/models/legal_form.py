from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Date, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class LegalForm(Base):
    __tablename__ = "legal_forms"

    id = Column(Integer, primary_key=True, index=True)
    
    # Form Information
    form_type = Column(String(50), nullable=False, index=True)
    # noim, birth_certificate, divorce_decree, death_certificate, etc.
    form_number = Column(String(100))
    
    # Status Information
    status = Column(String(50), default="required", index=True)
    # required, submitted, approved, expired, rejected
    
    # Dates
    required_date = Column(Date)
    submitted_date = Column(Date)
    approved_date = Column(Date)
    expiry_date = Column(Date)
    deadline_date = Column(Date)  # When it must be completed by
    
    # Document Information
    issuing_authority = Column(String(255))
    document_number = Column(String(100))
    file_path = Column(String(500))  # Path to uploaded document
    file_name = Column(String(255))
    
    # Additional Information
    notes = Column(Text)
    internal_notes = Column(Text)
    
    # Relationships
    couple_id = Column(Integer, ForeignKey("couples.id"), nullable=False)
    couple = relationship("Couple", back_populates="legal_forms")
    
    ceremony_id = Column(Integer, ForeignKey("ceremonies.id"))
    ceremony = relationship("Ceremony", back_populates="legal_forms")
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="legal_forms")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    @property
    def is_overdue(self):
        """Check if form is overdue."""
        from datetime import date
        return (self.deadline_date and 
                self.deadline_date < date.today() and 
                self.status not in ["approved", "submitted"])
    
    @property
    def days_until_deadline(self):
        """Calculate days until deadline."""
        from datetime import date
        if self.deadline_date:
            delta = self.deadline_date - date.today()
            return delta.days
        return None
    
    @property
    def is_expiring_soon(self):
        """Check if form expires within 30 days."""
        from datetime import date, timedelta
        if self.expiry_date:
            warning_date = date.today() + timedelta(days=30)
            return self.expiry_date <= warning_date
        return False
    
    def __repr__(self):
        return f"<LegalForm(id={self.id}, type='{self.form_type}', status='{self.status}')>"


# Add relationships to other models
from .couple import Couple
Couple.legal_forms = relationship("LegalForm", back_populates="couple")

from .ceremony import Ceremony
Ceremony.legal_forms = relationship("LegalForm", back_populates="ceremony")

from .user import User
User.legal_forms = relationship("LegalForm", back_populates="user") 