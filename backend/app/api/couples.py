from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Optional, List
from math import ceil
from app.database import get_db
from app.models.user import User
from app.models.couple import Couple
from app.schemas.couple import (
    CoupleCreate, CoupleUpdate, CoupleResponse, CoupleListResponse, 
    CoupleSearchParams, CoupleStatus
)
from app.auth.dependencies import get_current_active_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=CoupleListResponse)
async def get_couples(
    search: Optional[str] = Query(None, description="Search couples by name or email"),
    status: Optional[CoupleStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get list of couples with search and pagination."""
    try:
        # Build query
        query = db.query(Couple).filter(Couple.user_id == current_user.id)
        
        # Apply search filter
        if search:
            search_filter = or_(
                Couple.partner_1_first_name.ilike(f"%{search}%"),
                Couple.partner_1_last_name.ilike(f"%{search}%"),
                Couple.partner_2_first_name.ilike(f"%{search}%"),
                Couple.partner_2_last_name.ilike(f"%{search}%"),
                Couple.partner_1_email.ilike(f"%{search}%"),
                Couple.partner_2_email.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        # Apply status filter
        if status:
            query = query.filter(Couple.status == status.value)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (page - 1) * per_page
        couples = query.order_by(Couple.created_at.desc()).offset(offset).limit(per_page).all()
        
        # Calculate pagination info
        pages = ceil(total / per_page) if total > 0 else 1
        
        # Convert to response format
        couple_responses = []
        for couple in couples:
            couple_dict = {
                **couple.__dict__,
                "full_names": couple.full_names,
                "primary_email": couple.primary_email,
                "primary_phone": couple.primary_phone
            }
            couple_responses.append(CoupleResponse.from_orm(type('obj', (object,), couple_dict)))
        
        return CoupleListResponse(
            couples=couple_responses,
            total=total,
            page=page,
            per_page=per_page,
            pages=pages
        )
    
    except Exception as e:
        logger.error(f"Error fetching couples: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch couples"
        )


@router.post("/", response_model=CoupleResponse)
async def create_couple(
    couple_data: CoupleCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new couple."""
    try:
        # Create new couple
        new_couple = Couple(
            **couple_data.dict(),
            user_id=current_user.id
        )
        
        db.add(new_couple)
        db.commit()
        db.refresh(new_couple)
        
        logger.info(f"Created new couple: {new_couple.full_names} by user {current_user.email}")
        
        # Return response with computed properties
        couple_dict = {
            **new_couple.__dict__,
            "full_names": new_couple.full_names,
            "primary_email": new_couple.primary_email,
            "primary_phone": new_couple.primary_phone
        }
        
        return CoupleResponse.from_orm(type('obj', (object,), couple_dict))
    
    except Exception as e:
        logger.error(f"Error creating couple: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create couple"
        )


@router.get("/{couple_id}", response_model=CoupleResponse)
async def get_couple(
    couple_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific couple by ID."""
    try:
        couple = db.query(Couple).filter(
            and_(Couple.id == couple_id, Couple.user_id == current_user.id)
        ).first()
        
        if not couple:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Couple not found"
            )
        
        # Return response with computed properties
        couple_dict = {
            **couple.__dict__,
            "full_names": couple.full_names,
            "primary_email": couple.primary_email,
            "primary_phone": couple.primary_phone
        }
        
        return CoupleResponse.from_orm(type('obj', (object,), couple_dict))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching couple {couple_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch couple"
        )


@router.put("/{couple_id}", response_model=CoupleResponse)
async def update_couple(
    couple_id: int,
    couple_update: CoupleUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a specific couple."""
    try:
        couple = db.query(Couple).filter(
            and_(Couple.id == couple_id, Couple.user_id == current_user.id)
        ).first()
        
        if not couple:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Couple not found"
            )
        
        # Update couple fields
        update_data = couple_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(couple, field, value)
        
        db.commit()
        db.refresh(couple)
        
        logger.info(f"Updated couple {couple.full_names} by user {current_user.email}")
        
        # Return response with computed properties
        couple_dict = {
            **couple.__dict__,
            "full_names": couple.full_names,
            "primary_email": couple.primary_email,
            "primary_phone": couple.primary_phone
        }
        
        return CoupleResponse.from_orm(type('obj', (object,), couple_dict))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating couple {couple_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update couple"
        )


@router.delete("/{couple_id}")
async def delete_couple(
    couple_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a specific couple."""
    try:
        couple = db.query(Couple).filter(
            and_(Couple.id == couple_id, Couple.user_id == current_user.id)
        ).first()
        
        if not couple:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Couple not found"
            )
        
        couple_names = couple.full_names
        db.delete(couple)
        db.commit()
        
        logger.info(f"Deleted couple {couple_names} by user {current_user.email}")
        
        return {"message": f"Couple {couple_names} deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting couple {couple_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete couple"
        )


@router.get("/{couple_id}/summary")
async def get_couple_summary(
    couple_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get couple summary with related data (ceremonies, invoices, legal forms)."""
    try:
        couple = db.query(Couple).filter(
            and_(Couple.id == couple_id, Couple.user_id == current_user.id)
        ).first()
        
        if not couple:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Couple not found"
            )
        
        # Get related data counts
        from app.models.ceremony import Ceremony
        from app.models.invoice import Invoice
        from app.models.legal_form import LegalForm
        
        ceremonies_count = db.query(Ceremony).filter(Ceremony.couple_id == couple_id).count()
        invoices_count = db.query(Invoice).filter(Invoice.couple_id == couple_id).count()
        legal_forms_count = db.query(LegalForm).filter(LegalForm.couple_id == couple_id).count()
        
        # Get upcoming ceremony
        upcoming_ceremony = db.query(Ceremony).filter(
            and_(
                Ceremony.couple_id == couple_id,
                Ceremony.ceremony_date >= db.func.current_date()
            )
        ).order_by(Ceremony.ceremony_date.asc()).first()
        
        return {
            "couple": {
                **couple.__dict__,
                "full_names": couple.full_names,
                "primary_email": couple.primary_email,
                "primary_phone": couple.primary_phone
            },
            "summary": {
                "ceremonies_count": ceremonies_count,
                "invoices_count": invoices_count,
                "legal_forms_count": legal_forms_count,
                "upcoming_ceremony": {
                    "id": upcoming_ceremony.id,
                    "date": upcoming_ceremony.ceremony_date,
                    "venue": upcoming_ceremony.venue_name,
                    "status": upcoming_ceremony.status
                } if upcoming_ceremony else None
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching couple summary {couple_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch couple summary"
        ) 