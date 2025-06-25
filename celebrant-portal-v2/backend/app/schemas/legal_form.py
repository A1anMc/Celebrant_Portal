from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class LegalFormType(str, Enum):
    noim = "noim"
    birth_certificate = "birth_certificate"
    divorce_decree = "divorce_decree"
    death_certificate = "death_certificate"
    statutory_declaration = "statutory_declaration"
    other = "other"


class LegalFormStatus(str, Enum):
    required = "required"
    submitted = "submitted"
    approved = "approved"
    expired = "expired"
    rejected = "rejected"


class LegalFormCreate(BaseModel):
    form_type: LegalFormType
    form_number: Optional[str] = None
    status: LegalFormStatus = LegalFormStatus.required
    
    # Dates
    required_date: Optional[date] = None
    submitted_date: Optional[date] = None
    approved_date: Optional[date] = None
    expiry_date: Optional[date] = None
    deadline_date: Optional[date] = None
    
    # Document info
    issuing_authority: Optional[str] = None
    document_number: Optional[str] = None
    file_name: Optional[str] = None
    
    # Notes
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    
    # Relationships
    couple_id: int
    ceremony_id: Optional[int] = None


class LegalFormUpdate(BaseModel):
    form_type: Optional[LegalFormType] = None
    form_number: Optional[str] = None
    status: Optional[LegalFormStatus] = None
    
    # Dates
    required_date: Optional[date] = None
    submitted_date: Optional[date] = None
    approved_date: Optional[date] = None
    expiry_date: Optional[date] = None
    deadline_date: Optional[date] = None
    
    # Document info
    issuing_authority: Optional[str] = None
    document_number: Optional[str] = None
    file_name: Optional[str] = None
    
    # Notes
    notes: Optional[str] = None
    internal_notes: Optional[str] = None


class LegalFormResponse(BaseModel):
    id: int
    form_type: str
    form_number: Optional[str] = None
    status: str
    
    # Dates
    required_date: Optional[date] = None
    submitted_date: Optional[date] = None
    approved_date: Optional[date] = None
    expiry_date: Optional[date] = None
    deadline_date: Optional[date] = None
    
    # Document info
    issuing_authority: Optional[str] = None
    document_number: Optional[str] = None
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    
    # Notes
    notes: Optional[str] = None
    internal_notes: Optional[str] = None
    
    # Relationships
    couple_id: int
    ceremony_id: Optional[int] = None
    
    # Computed properties
    is_overdue: bool
    days_until_deadline: Optional[int] = None
    is_expiring_soon: bool
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LegalFormListResponse(BaseModel):
    legal_forms: List[LegalFormResponse]
    total: int
    page: int
    per_page: int
    pages: int


class NOIMTrackingResponse(BaseModel):
    """Specialized response for NOIM tracking dashboard."""
    id: int
    couple_names: str
    ceremony_date: Optional[date] = None
    noim_status: str
    submitted_date: Optional[date] = None
    approved_date: Optional[date] = None
    expiry_date: Optional[date] = None
    deadline_date: Optional[date] = None
    days_until_deadline: Optional[int] = None
    is_overdue: bool
    is_expiring_soon: bool
    venue_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class LegalComplianceStatus(BaseModel):
    """Overall legal compliance status for a couple/ceremony."""
    couple_id: int
    ceremony_id: Optional[int] = None
    couple_names: str
    ceremony_date: Optional[date] = None
    
    # Compliance status
    overall_status: str  # compliant, pending, overdue, incomplete
    required_forms: List[str]
    completed_forms: List[str]
    pending_forms: List[str]
    overdue_forms: List[str]
    
    # NOIM specific
    noim_required: bool
    noim_status: Optional[str] = None
    noim_deadline: Optional[date] = None
    
    # Alerts
    urgent_actions: List[str]
    warnings: List[str] 