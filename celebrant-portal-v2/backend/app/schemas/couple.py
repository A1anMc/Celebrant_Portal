from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class CoupleStatus(str, Enum):
    """Enum for couple status values."""
    INQUIRY = "inquiry"
    CONSULTATION = "consultation"
    BOOKED = "booked"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CoupleSearchParams(BaseModel):
    """Search parameters for couples."""
    search: Optional[str] = None
    status: Optional[CoupleStatus] = None
    page: int = 1
    per_page: int = 20


class CoupleBase(BaseModel):
    # Partner 1 details
    partner_1_first_name: str
    partner_1_last_name: str
    partner_1_phone: Optional[str] = None
    partner_1_email: Optional[str] = None
    partner_1_address: Optional[str] = None
    partner_1_date_of_birth: Optional[date] = None
    
    # Partner 2 details
    partner_2_first_name: str
    partner_2_last_name: str
    partner_2_phone: Optional[str] = None
    partner_2_email: Optional[str] = None
    partner_2_address: Optional[str] = None
    partner_2_date_of_birth: Optional[date] = None
    
    # Relationship Information
    relationship_start_date: Optional[date] = None
    previous_marriages: Optional[str] = None
    
    # Contact preferences
    primary_contact: str = "partner_1"  # partner_1 or partner_2
    preferred_contact_method: str = "email"  # email, phone, text
    
    # Status and Notes
    status: str = "inquiry"
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    
    # Source and Marketing
    referral_source: Optional[str] = None
    marketing_consent: str = "not_specified"


class CoupleCreate(CoupleBase):
    pass


class CoupleUpdate(BaseModel):
    # Partner 1 details
    partner_1_first_name: Optional[str] = None
    partner_1_last_name: Optional[str] = None
    partner_1_phone: Optional[str] = None
    partner_1_email: Optional[str] = None
    partner_1_address: Optional[str] = None
    partner_1_date_of_birth: Optional[date] = None
    
    # Partner 2 details
    partner_2_first_name: Optional[str] = None
    partner_2_last_name: Optional[str] = None
    partner_2_phone: Optional[str] = None
    partner_2_email: Optional[str] = None
    partner_2_address: Optional[str] = None
    partner_2_date_of_birth: Optional[date] = None
    
    # Relationship Information
    relationship_start_date: Optional[date] = None
    previous_marriages: Optional[str] = None
    
    # Contact preferences
    primary_contact: Optional[str] = None
    preferred_contact_method: Optional[str] = None
    
    # Status and Notes
    status: Optional[str] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    
    # Source and Marketing
    referral_source: Optional[str] = None
    marketing_consent: Optional[str] = None


class CoupleResponse(CoupleBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Computed properties
    full_names: Optional[str] = None
    primary_email: Optional[str] = None
    primary_phone: Optional[str] = None


class CoupleListResponse(BaseModel):
    couples: List[CoupleResponse]
    total: int
    page: int
    per_page: int
    pages: int 