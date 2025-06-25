from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class CoupleStatus(str, Enum):
    inquiry = "inquiry"
    consultation = "consultation"
    booked = "booked"
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"


class PrimaryContact(str, Enum):
    partner_1 = "partner_1"
    partner_2 = "partner_2"


class ContactMethod(str, Enum):
    email = "email"
    phone = "phone"
    text = "text"


class CoupleCreate(BaseModel):
    # Partner 1
    partner_1_first_name: str
    partner_1_last_name: str
    partner_1_email: Optional[EmailStr] = None
    partner_1_phone: Optional[str] = None
    partner_1_date_of_birth: Optional[date] = None
    partner_1_address: Optional[str] = None
    
    # Partner 2
    partner_2_first_name: str
    partner_2_last_name: str
    partner_2_email: Optional[EmailStr] = None
    partner_2_phone: Optional[str] = None
    partner_2_date_of_birth: Optional[date] = None
    partner_2_address: Optional[str] = None
    
    # Relationship info
    relationship_start_date: Optional[date] = None
    previous_marriages: Optional[str] = None
    
    # Contact preferences
    primary_contact: PrimaryContact = PrimaryContact.partner_1
    preferred_contact_method: ContactMethod = ContactMethod.email
    
    # Status and notes
    status: CoupleStatus = CoupleStatus.inquiry
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    
    # Marketing
    referral_source: Optional[str] = None
    marketing_consent: Optional[str] = "not_specified"


class CoupleUpdate(BaseModel):
    # Partner 1
    partner_1_first_name: Optional[str] = None
    partner_1_last_name: Optional[str] = None
    partner_1_email: Optional[EmailStr] = None
    partner_1_phone: Optional[str] = None
    partner_1_date_of_birth: Optional[date] = None
    partner_1_address: Optional[str] = None
    
    # Partner 2
    partner_2_first_name: Optional[str] = None
    partner_2_last_name: Optional[str] = None
    partner_2_email: Optional[EmailStr] = None
    partner_2_phone: Optional[str] = None
    partner_2_date_of_birth: Optional[date] = None
    partner_2_address: Optional[str] = None
    
    # Relationship info
    relationship_start_date: Optional[date] = None
    previous_marriages: Optional[str] = None
    
    # Contact preferences
    primary_contact: Optional[PrimaryContact] = None
    preferred_contact_method: Optional[ContactMethod] = None
    
    # Status and notes
    status: Optional[CoupleStatus] = None
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    
    # Marketing
    referral_source: Optional[str] = None
    marketing_consent: Optional[str] = None


class CoupleResponse(BaseModel):
    id: int
    
    # Partner 1
    partner_1_first_name: str
    partner_1_last_name: str
    partner_1_email: Optional[str] = None
    partner_1_phone: Optional[str] = None
    partner_1_date_of_birth: Optional[date] = None
    partner_1_address: Optional[str] = None
    
    # Partner 2
    partner_2_first_name: str
    partner_2_last_name: str
    partner_2_email: Optional[str] = None
    partner_2_phone: Optional[str] = None
    partner_2_date_of_birth: Optional[date] = None
    partner_2_address: Optional[str] = None
    
    # Relationship info
    relationship_start_date: Optional[date] = None
    previous_marriages: Optional[str] = None
    
    # Contact preferences
    primary_contact: str
    preferred_contact_method: str
    
    # Status and notes
    status: str
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    
    # Marketing
    referral_source: Optional[str] = None
    marketing_consent: str
    
    # Computed properties
    full_names: str
    primary_email: Optional[str] = None
    primary_phone: Optional[str] = None
    
    # Timestamps
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


class CoupleSearchParams(BaseModel):
    search: Optional[str] = None
    status: Optional[CoupleStatus] = None
    page: int = 1
    per_page: int = 20 