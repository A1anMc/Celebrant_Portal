from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    
    # Enhanced user fields
    role = Column(String(50), default="celebrant")  # celebrant, admin, assistant
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Profile information
    phone = Column(String(20))
    business_name = Column(String(255))
    abn = Column(String(20))
    address = Column(Text)
    
    # Preferences
    timezone = Column(String(50), default="Australia/Melbourne")
    currency = Column(String(3), default="AUD")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>" 