from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from math import ceil
from datetime import date, timedelta
from app.database import get_db
from app.models.user import User
from app.models.couple import Couple
from app.models.ceremony import Ceremony
from app.models.legal_form import LegalForm
from app.schemas.legal_form import (
    LegalFormCreate, LegalFormUpdate, LegalFormResponse, LegalFormListResponse,
    NOIMTrackingResponse, LegalComplianceStatus, LegalFormType, LegalFormStatus
)
from app.auth.dependencies import get_current_active_user
import logging
import os
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=LegalFormListResponse)
async def get_legal_forms(
    form_type: Optional[LegalFormType] = Query(None, description="Filter by form type"),
    status: Optional[LegalFormStatus] = Query(None, description="Filter by status"),
    urgent: Optional[bool] = Query(None, description="Show only urgent forms"),
    couple_id: Optional[int] = Query(None, description="Filter by couple"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of legal forms with filtering and pagination."""
    try:
        # Build query
        query = db.query(LegalForm).filter(LegalForm.user_id == current_user.id)
        
        # Apply filters
        if form_type:
            query = query.filter(LegalForm.form_type == form_type.value)
        
        if status:
            query = query.filter(LegalForm.status == status.value)
        
        if couple_id:
            query = query.filter(LegalForm.couple_id == couple_id)
        
        if urgent:
            today = date.today()
            urgent_filter = or_(
                and_(
                    LegalForm.deadline_date.isnot(None),
                    LegalForm.deadline_date <= today + timedelta(days=7)
                ),
                and_(
                    LegalForm.expiry_date.isnot(None),
                    LegalForm.expiry_date <= today + timedelta(days=30)
                )
            )
            query = query.filter(urgent_filter)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        legal_forms = query.order_by(LegalForm.deadline_date.asc().nullslast()).offset(offset).limit(per_page).all()
        
        # Calculate pagination info
        pages = ceil(total / per_page) if total > 0 else 1
        
        # Convert to response format
        form_responses = []
        for form in legal_forms:
            form_dict = {
                **form.__dict__,
                "is_overdue": form.is_overdue,
                "days_until_deadline": form.days_until_deadline,
                "is_expiring_soon": form.is_expiring_soon
            }
            form_responses.append(LegalFormResponse.from_orm(type('obj', (object,), form_dict)))
        
        return LegalFormListResponse(
            legal_forms=form_responses,
            total=total,
            page=page,
            per_page=per_page,
            pages=pages
        )
    
    except Exception as e:
        logger.error(f"Error fetching legal forms: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch legal forms"
        )


@router.post("/", response_model=LegalFormResponse)
async def create_legal_form(
    form_data: LegalFormCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new legal form."""
    try:
        # Verify couple belongs to user
        couple = db.query(Couple).filter(
            and_(Couple.id == form_data.couple_id, Couple.user_id == current_user.id)
        ).first()
        
        if not couple:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Couple not found"
            )
        
        # Create new legal form
        new_form = LegalForm(
            **form_data.dict(),
            user_id=current_user.id
        )
        
        db.add(new_form)
        db.commit()
        db.refresh(new_form)
        
        logger.info(f"Created legal form {new_form.form_type} for couple {couple.full_names}")
        
        # Return response with computed properties
        form_dict = {
            **new_form.__dict__,
            "is_overdue": new_form.is_overdue,
            "days_until_deadline": new_form.days_until_deadline,
            "is_expiring_soon": new_form.is_expiring_soon
        }
        
        return LegalFormResponse.from_orm(type('obj', (object,), form_dict))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating legal form: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create legal form"
        )


@router.get("/noim-tracking", response_model=List[NOIMTrackingResponse])
async def get_noim_tracking(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get NOIM tracking dashboard with all NOIM forms and their status."""
    try:
        # Get all NOIM forms with couple and ceremony details
        noim_forms = db.query(LegalForm).join(Couple).outerjoin(Ceremony).filter(
            and_(
                LegalForm.user_id == current_user.id,
                LegalForm.form_type == "noim"
            )
        ).order_by(LegalForm.deadline_date.asc().nullslast()).all()
        
        tracking_data = []
        for form in noim_forms:
            ceremony = None
            if form.ceremony_id:
                ceremony = db.query(Ceremony).filter(Ceremony.id == form.ceremony_id).first()
            
            tracking_data.append({
                "id": form.id,
                "couple_names": form.couple.full_names,
                "ceremony_date": ceremony.ceremony_date if ceremony else None,
                "noim_status": form.status,
                "submitted_date": form.submitted_date,
                "approved_date": form.approved_date,
                "expiry_date": form.expiry_date,
                "deadline_date": form.deadline_date,
                "days_until_deadline": form.days_until_deadline,
                "is_overdue": form.is_overdue,
                "is_expiring_soon": form.is_expiring_soon,
                "venue_name": ceremony.venue_name if ceremony else None
            })
        
        return [NOIMTrackingResponse(**data) for data in tracking_data]
    
    except Exception as e:
        logger.error(f"Error fetching NOIM tracking: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch NOIM tracking"
        )


@router.get("/compliance-status")
async def get_compliance_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get overall legal compliance status for all couples."""
    try:
        # Get all couples with their legal forms
        couples = db.query(Couple).filter(Couple.user_id == current_user.id).all()
        
        compliance_statuses = []
        for couple in couples:
            # Get all legal forms for this couple
            legal_forms = db.query(LegalForm).filter(LegalForm.couple_id == couple.id).all()
            
            # Get ceremony if exists
            ceremony = db.query(Ceremony).filter(Ceremony.couple_id == couple.id).first()
            
            # Analyze compliance
            required_forms = ["noim"]  # Basic requirement
            completed_forms = []
            pending_forms = []
            overdue_forms = []
            
            noim_required = True
            noim_status = None
            noim_deadline = None
            
            for form in legal_forms:
                if form.form_type == "noim":
                    noim_status = form.status
                    noim_deadline = form.deadline_date
                    
                    if form.status in ["approved"]:
                        completed_forms.append(form.form_type)
                    elif form.status in ["required", "submitted"]:
                        if form.is_overdue:
                            overdue_forms.append(form.form_type)
                        else:
                            pending_forms.append(form.form_type)
                else:
                    if form.status in ["approved"]:
                        completed_forms.append(form.form_type)
                    elif form.status in ["required", "submitted"]:
                        if form.is_overdue:
                            overdue_forms.append(form.form_type)
                        else:
                            pending_forms.append(form.form_type)
            
            # Determine overall status
            if overdue_forms:
                overall_status = "overdue"
            elif not noim_status and noim_required:
                overall_status = "incomplete"
            elif pending_forms:
                overall_status = "pending"
            else:
                overall_status = "compliant"
            
            # Generate alerts
            urgent_actions = []
            warnings = []
            
            if noim_status in ["required"] and noim_deadline:
                days_until = (noim_deadline - date.today()).days
                if days_until <= 0:
                    urgent_actions.append(f"NOIM is overdue by {abs(days_until)} days")
                elif days_until <= 7:
                    urgent_actions.append(f"NOIM due in {days_until} days")
                elif days_until <= 14:
                    warnings.append(f"NOIM due in {days_until} days")
            
            compliance_statuses.append(LegalComplianceStatus(
                couple_id=couple.id,
                ceremony_id=ceremony.id if ceremony else None,
                couple_names=couple.full_names,
                ceremony_date=ceremony.ceremony_date if ceremony else None,
                overall_status=overall_status,
                required_forms=required_forms,
                completed_forms=completed_forms,
                pending_forms=pending_forms,
                overdue_forms=overdue_forms,
                noim_required=noim_required,
                noim_status=noim_status,
                noim_deadline=noim_deadline,
                urgent_actions=urgent_actions,
                warnings=warnings
            ))
        
        return compliance_statuses
    
    except Exception as e:
        logger.error(f"Error fetching compliance status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch compliance status"
        )


@router.put("/{form_id}", response_model=LegalFormResponse)
async def update_legal_form(
    form_id: int,
    form_update: LegalFormUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a legal form."""
    try:
        legal_form = db.query(LegalForm).filter(
            and_(LegalForm.id == form_id, LegalForm.user_id == current_user.id)
        ).first()
        
        if not legal_form:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Legal form not found"
            )
        
        # Update form fields
        update_data = form_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(legal_form, field, value)
        
        db.commit()
        db.refresh(legal_form)
        
        logger.info(f"Updated legal form {legal_form.form_type} (ID: {form_id})")
        
        # Return response with computed properties
        form_dict = {
            **legal_form.__dict__,
            "is_overdue": legal_form.is_overdue,
            "days_until_deadline": legal_form.days_until_deadline,
            "is_expiring_soon": legal_form.is_expiring_soon
        }
        
        return LegalFormResponse.from_orm(type('obj', (object,), form_dict))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating legal form {form_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update legal form"
        )


@router.delete("/{form_id}")
async def delete_legal_form(
    form_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a legal form."""
    try:
        legal_form = db.query(LegalForm).filter(
            and_(LegalForm.id == form_id, LegalForm.user_id == current_user.id)
        ).first()
        
        if not legal_form:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Legal form not found"
            )
        
        form_type = legal_form.form_type
        db.delete(legal_form)
        db.commit()
        
        logger.info(f"Deleted legal form {form_type} (ID: {form_id})")
        
        return {"message": f"Legal form {form_type} deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting legal form {form_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete legal form"
        ) 