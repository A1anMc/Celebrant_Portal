from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


class CoupleBase(BaseModel):
    # Partner 1 details
    partner_1_name: str
    partner_1_phone: Optional[str] = None
    partner_1_email: Optional[str] = None
    partner_1_address: Optional[str] = None
    partner_1_occupation: Optional[str] = None
    partner_1_birth_date: Optional[date] = None
    partner_1_birth_place: Optional[str] = None
    partner_1_parents: Optional[str] = None
    
    # Partner 2 details
    partner_2_name: str
    partner_2_phone: Optional[str] = None
    partner_2_email: Optional[str] = None
    partner_2_address: Optional[str] = None
    partner_2_occupation: Optional[str] = None
    partner_2_birth_date: Optional[date] = None
    partner_2_birth_place: Optional[str] = None
    partner_2_parents: Optional[str] = None
    
    # Ceremony details
    ceremony_date: Optional[datetime] = None
    ceremony_venue: Optional[str] = None
    ceremony_address: Optional[str] = None
    ceremony_type: str = "wedding"  # wedding, commitment, renewal
    ceremony_style: Optional[str] = None  # traditional, modern, themed, etc.
    
    # Contact preferences
    preferred_contact_method: str = "email"  # email, phone, sms
    notes: Optional[str] = None


class CoupleCreate(CoupleBase):
    pass


class CoupleUpdate(BaseModel):
    # Partner 1 details
    partner_1_name: Optional[str] = None
    partner_1_phone: Optional[str] = None
    partner_1_email: Optional[str] = None
    partner_1_address: Optional[str] = None
    partner_1_occupation: Optional[str] = None
    partner_1_birth_date: Optional[date] = None
    partner_1_birth_place: Optional[str] = None
    partner_1_parents: Optional[str] = None
    
    # Partner 2 details
    partner_2_name: Optional[str] = None
    partner_2_phone: Optional[str] = None
    partner_2_email: Optional[str] = None
    partner_2_address: Optional[str] = None
    partner_2_occupation: Optional[str] = None
    partner_2_birth_date: Optional[date] = None
    partner_2_birth_place: Optional[str] = None
    partner_2_parents: Optional[str] = None
    
    # Ceremony details
    ceremony_date: Optional[datetime] = None
    ceremony_venue: Optional[str] = None
    ceremony_address: Optional[str] = None
    ceremony_type: Optional[str] = None
    ceremony_style: Optional[str] = None
    
    # Contact preferences
    preferred_contact_method: Optional[str] = None
    notes: Optional[str] = None
    
    # Status
    status: Optional[str] = None


class CoupleResponse(CoupleBase):
    id: int
    user_id: int
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CoupleListResponse(BaseModel):
    couples: List[CoupleResponse]
    total: int
    page: int
    per_page: int
    pages: int 