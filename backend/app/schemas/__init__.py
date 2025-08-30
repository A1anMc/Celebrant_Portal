# Schemas package
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Couple schemas
class CoupleBase(BaseModel):
    partner1_name: str
    partner1_email: EmailStr
    partner1_phone: Optional[str] = None
    partner2_name: str
    partner2_email: EmailStr
    partner2_phone: Optional[str] = None
    wedding_date: Optional[datetime] = None
    venue: Optional[str] = None
    ceremony_type: str = "Wedding"
    status: str = "Inquiry"
    notes: Optional[str] = None

class CoupleCreate(CoupleBase):
    pass

class CoupleUpdate(BaseModel):
    partner1_name: Optional[str] = None
    partner1_email: Optional[EmailStr] = None
    partner1_phone: Optional[str] = None
    partner2_name: Optional[str] = None
    partner2_email: Optional[EmailStr] = None
    partner2_phone: Optional[str] = None
    wedding_date: Optional[datetime] = None
    venue: Optional[str] = None
    ceremony_type: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class Couple(CoupleBase):
    id: int
    celebrant_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Ceremony schemas
class CeremonyBase(BaseModel):
    ceremony_script: Optional[str] = None
    vows_partner1: Optional[str] = None
    vows_partner2: Optional[str] = None
    ring_exchange: Optional[str] = None
    special_readings: Optional[str] = None
    music_notes: Optional[str] = None

class CeremonyCreate(CeremonyBase):
    couple_id: int

class CeremonyUpdate(CeremonyBase):
    pass

class Ceremony(CeremonyBase):
    id: int
    couple_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Invoice schemas
class InvoiceBase(BaseModel):
    invoice_number: str
    amount: float
    status: str = "Draft"
    due_date: Optional[datetime] = None
    paid_date: Optional[datetime] = None
    notes: Optional[str] = None

class InvoiceCreate(InvoiceBase):
    couple_id: int

class InvoiceUpdate(BaseModel):
    invoice_number: Optional[str] = None
    amount: Optional[float] = None
    status: Optional[str] = None
    due_date: Optional[datetime] = None
    paid_date: Optional[datetime] = None
    notes: Optional[str] = None

class Invoice(InvoiceBase):
    id: int
    couple_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Response schemas
class Message(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    detail: str

# Note schemas
class NoteBase(BaseModel):
    content: str

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    content: Optional[str] = None

class Note(NoteBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 