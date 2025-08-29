"""CRM Models for Melbourne Celebrant Portal"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from enum import Enum


class LeadStage(str, Enum):
    """Lead pipeline stages"""
    INITIAL_CONTACT = "initial_contact"
    CONSULTATION_SCHEDULED = "consultation_scheduled"
    PROPOSAL_SENT = "proposal_sent"
    CONTRACT_SIGNED = "contract_signed"
    CEREMONY_COMPLETED = "ceremony_completed"
    LOST = "lost"


class CommunicationType(str, Enum):
    """Types of communication"""
    EMAIL = "email"
    PHONE = "phone"
    SMS = "sms"
    IN_PERSON = "in_person"
    VIDEO_CALL = "video_call"


class TaskPriority(str, Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskStatus(str, Enum):
    """Task status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# Base Models
class CommunicationLogBase(BaseModel):
    """Base communication log model"""
    communication_type: CommunicationType
    subject: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    sent_at: Optional[datetime] = None
    status: Optional[str] = Field(None, max_length=50)


class TaskBase(BaseModel):
    """Base task model"""
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    couple_id: Optional[int] = None


class EmailTemplateBase(BaseModel):
    """Base email template model"""
    name: str = Field(..., max_length=100)
    subject: str = Field(..., max_length=200)
    content: str
    template_type: Optional[str] = Field(None, max_length=50)
    is_active: bool = True


# Create Models
class CommunicationLogCreate(CommunicationLogBase):
    """Create communication log"""
    couple_id: int


class TaskCreate(TaskBase):
    """Create task"""
    user_id: int


class EmailTemplateCreate(EmailTemplateBase):
    """Create email template"""
    user_id: int


# Update Models
class CommunicationLogUpdate(BaseModel):
    """Update communication log"""
    communication_type: Optional[CommunicationType] = None
    subject: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    sent_at: Optional[datetime] = None
    status: Optional[str] = Field(None, max_length=50)


class TaskUpdate(BaseModel):
    """Update task"""
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    couple_id: Optional[int] = None


class EmailTemplateUpdate(BaseModel):
    """Update email template"""
    name: Optional[str] = Field(None, max_length=100)
    subject: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = None
    template_type: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


# Response Models
class CommunicationLogResponse(CommunicationLogBase):
    """Communication log response"""
    id: int
    couple_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaskResponse(TaskBase):
    """Task response"""
    id: int
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EmailTemplateResponse(EmailTemplateBase):
    """Email template response"""
    id: int
    user_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Enhanced Couple Models
class CoupleCRMUpdate(BaseModel):
    """Update couple with CRM fields"""
    lead_stage: Optional[LeadStage] = None
    lead_source: Optional[str] = Field(None, max_length=100)
    follow_up_date: Optional[date] = None
    estimated_value: Optional[Decimal] = Field(None, ge=0)
    notes: Optional[str] = None

    @validator('estimated_value')
    def validate_estimated_value(cls, v):
        if v is not None and v < 0:
            raise ValueError('Estimated value must be positive')
        return v


# Dashboard Models
class DashboardStats(BaseModel):
    """Dashboard statistics"""
    total_couples: int
    active_leads: int
    pending_tasks: int
    total_revenue: Decimal
    monthly_revenue: Decimal
    conversion_rate: float

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }


class LeadPipelineStats(BaseModel):
    """Lead pipeline statistics"""
    stage: LeadStage
    count: int
    value: Decimal

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v)
        }
