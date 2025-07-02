from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    couples = relationship("Couple", back_populates="celebrant")

class Couple(Base):
    __tablename__ = "couples"
    
    id = Column(Integer, primary_key=True, index=True)
    partner1_name = Column(String, nullable=False)
    partner1_email = Column(String, nullable=False)
    partner1_phone = Column(String)
    partner2_name = Column(String, nullable=False)
    partner2_email = Column(String, nullable=False)
    partner2_phone = Column(String)
    wedding_date = Column(DateTime)
    venue = Column(String)
    ceremony_type = Column(String, default="Wedding")
    status = Column(String, default="Inquiry")  # Inquiry, Booked, Completed
    notes = Column(Text)
    celebrant_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    celebrant = relationship("User", back_populates="couples")
    ceremonies = relationship("Ceremony", back_populates="couple")
    invoices = relationship("Invoice", back_populates="couple")

class Ceremony(Base):
    __tablename__ = "ceremonies"
    
    id = Column(Integer, primary_key=True, index=True)
    couple_id = Column(Integer, ForeignKey("couples.id"))
    ceremony_script = Column(Text)
    vows_partner1 = Column(Text)
    vows_partner2 = Column(Text)
    ring_exchange = Column(Text)
    special_readings = Column(Text)
    music_notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    couple = relationship("Couple", back_populates="ceremonies")

class Invoice(Base):
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    couple_id = Column(Integer, ForeignKey("couples.id"))
    invoice_number = Column(String, unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default="Draft")  # Draft, Sent, Paid, Overdue
    due_date = Column(DateTime)
    paid_date = Column(DateTime)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    couple = relationship("Couple", back_populates="invoices")

class FailedLoginAttempt(Base):
    __tablename__ = "failed_login_attempts"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_revoked = Column(Boolean, default=False)
    
    user = relationship("User") 