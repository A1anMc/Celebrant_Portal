from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class CeremonyTemplate(Base):
    __tablename__ = "ceremony_templates"

    id = Column(Integer, primary_key=True, index=True)
    
    # Template Information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(50), default="general")  # traditional, modern, beach, garden, etc.
    
    # Template Content
    content = Column(Text, nullable=False)  # Main ceremony script
    welcome_words = Column(Text)
    introduction = Column(Text)
    vows_section = Column(Text)
    ring_exchange_section = Column(Text)
    unity_ceremony_section = Column(Text)
    pronouncement = Column(Text)
    closing_words = Column(Text)
    
    # Template Properties
    estimated_duration = Column(Integer, default=20)  # minutes
    is_public = Column(Boolean, default=True)  # Available to all users
    is_active = Column(Boolean, default=True)
    
    # Usage Statistics
    usage_count = Column(Integer, default=0)
    
    # Relationships
    user_id = Column(Integer, ForeignKey("users.id"))  # Creator (null for system templates)
    user = relationship("User", back_populates="templates")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    @property
    def is_system_template(self):
        """Check if this is a system-provided template."""
        return self.user_id is None
    
    @property
    def word_count(self):
        """Calculate approximate word count of template."""
        if self.content:
            return len(self.content.split())
        return 0
    
    def __repr__(self):
        return f"<CeremonyTemplate(id={self.id}, name='{self.name}', category='{self.category}')>"


# Add relationships to other models
from .user import User
User.templates = relationship("CeremonyTemplate", back_populates="user")

from .ceremony import Ceremony
CeremonyTemplate.ceremonies = relationship("Ceremony", back_populates="template") 