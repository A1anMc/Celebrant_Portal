from sqlalchemy import Column, Integer, String, DateTime, Text, Numeric, ForeignKey, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Couple(Base):
    __tablename__ = "couples"

    id = Column(Integer, primary_key=True, index=True)
    
    # Partner 1 Information
    partner_1_first_name = Column(String(100), nullable=False)
    partner_1_last_name = Column(String(100), nullable=False)
    partner_1_email = Column(String(255), index=True)
    partner_1_phone = Column(String(20))
    partner_1_date_of_birth = Column(Date)
    partner_1_address = Column(Text)
    
    # Partner 2 Information
    partner_2_first_name = Column(String(100), nullable=False)
    partner_2_last_name = Column(String(100), nullable=False)
    partner_2_email = Column(String(255), index=True)
    partner_2_phone = Column(String(20))
    partner_2_date_of_birth = Column(Date)
    partner_2_address = Column(Text)
    
    # Relationship Information
    relationship_start_date = Column(Date)
    previous_marriages = Column(Text)  # JSON string for complex data
    
    # Contact Preferences
    primary_contact = Column(String(10), default="partner_1")  # partner_1 or partner_2
    preferred_contact_method = Column(String(20), default="email")  # email, phone, text
    
    # Status and Notes
    status = Column(String(50), default="inquiry", index=True)
    # inquiry, consultation, booked, confirmed, completed, cancelled
    notes = Column(Text)
    internal_notes = Column(Text)  # Private notes not visible to clients
    
    # Source and Marketing
    referral_source = Column(String(100))
    marketing_consent = Column(String(20), default="not_specified")
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="couples")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    @property
    def full_names(self):
        """Return formatted couple names."""
        return f"{self.partner_1_first_name} {self.partner_1_last_name} & {self.partner_2_first_name} {self.partner_2_last_name}"
    
    @property
    def primary_email(self):
        """Return primary contact email."""
        if self.primary_contact == "partner_2" and self.partner_2_email:
            return self.partner_2_email
        return self.partner_1_email or self.partner_2_email
    
    @property
    def primary_phone(self):
        """Return primary contact phone."""
        if self.primary_contact == "partner_2" and self.partner_2_phone:
            return self.partner_2_phone
        return self.partner_1_phone or self.partner_2_phone
    
    def __repr__(self):
        return f"<Couple(id={self.id}, names='{self.full_names}', status='{self.status}')>"


# Add relationship to User model
from .user import User
User.couples = relationship("Couple", back_populates="user") 