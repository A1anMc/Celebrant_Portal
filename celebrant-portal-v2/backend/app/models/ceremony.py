from sqlalchemy import Column, Integer, String, DateTime, Text, Numeric, ForeignKey, Date, Time, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Ceremony(Base):
    __tablename__ = "ceremonies"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    ceremony_date = Column(Date, nullable=False, index=True)
    ceremony_time = Column(Time, nullable=False)
    estimated_duration = Column(Integer, default=30)  # minutes
    
    # Venue Information
    venue_name = Column(String(255))
    venue_address = Column(Text)
    venue_contact_name = Column(String(100))
    venue_contact_phone = Column(String(20))
    venue_contact_email = Column(String(255))
    
    # Ceremony Details
    ceremony_type = Column(String(50), default="civil")  # civil, religious, commitment, renewal
    style = Column(String(50))  # traditional, modern, beach, garden, etc.
    guest_count = Column(Integer)
    special_requirements = Column(Text)
    
    # Legal Requirements
    noim_lodged = Column(Boolean, default=False)
    noim_lodged_date = Column(Date)
    noim_expiry_date = Column(Date)
    
    # Ceremony Content
    vows_type = Column(String(50), default="traditional")  # traditional, personal, mixed
    ring_exchange = Column(Boolean, default=True)
    unity_ceremony = Column(String(50))  # candle, sand, handfasting, etc.
    readings = Column(Text)  # JSON string for multiple readings
    music_requests = Column(Text)
    
    # Rehearsal
    rehearsal_required = Column(Boolean, default=False)
    rehearsal_date = Column(Date)
    rehearsal_time = Column(Time)
    rehearsal_location = Column(String(255))
    
    # Financial
    ceremony_fee = Column(Numeric(10, 2), default=0)
    travel_fee = Column(Numeric(10, 2), default=0)
    additional_fees = Column(Numeric(10, 2), default=0)
    total_fee = Column(Numeric(10, 2), default=0)
    
    # Status
    status = Column(String(50), default="planned", index=True)
    # planned, confirmed, completed, cancelled
    
    # Notes
    ceremony_notes = Column(Text)
    internal_notes = Column(Text)
    
    # Relationships
    couple_id = Column(Integer, ForeignKey("couples.id"), nullable=False)
    couple = relationship("Couple", back_populates="ceremonies")
    
    template_id = Column(Integer, ForeignKey("ceremony_templates.id"))
    template = relationship("CeremonyTemplate", back_populates="ceremonies")
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="ceremonies")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    @property
    def total_calculated_fee(self):
        """Calculate total fee from components."""
        return (self.ceremony_fee or 0) + (self.travel_fee or 0) + (self.additional_fees or 0)
    
    @property
    def is_upcoming(self):
        """Check if ceremony is in the future."""
        from datetime import date
        return self.ceremony_date > date.today()
    
    @property
    def days_until_ceremony(self):
        """Calculate days until ceremony."""
        from datetime import date
        if self.ceremony_date:
            delta = self.ceremony_date - date.today()
            return delta.days
        return None
    
    def __repr__(self):
        return f"<Ceremony(id={self.id}, date='{self.ceremony_date}', couple_id={self.couple_id})>"


# Add relationships to other models
from .couple import Couple
Couple.ceremonies = relationship("Ceremony", back_populates="couple")

from .user import User
User.ceremonies = relationship("Ceremony", back_populates="user") 