from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime
from ...core.database import get_db
from ...models import User, Couple
from ...schemas import CoupleCreate, CoupleUpdate, Couple as CoupleSchema
from ...core.auth import get_current_active_user
from ...services.couple_service import CoupleService
from ...core.exceptions import (
    CoupleNotFoundException,
    ValidationException,
    DatabaseException
)

router = APIRouter(prefix="/couples", tags=["couples"])

@router.post("/", response_model=CoupleSchema, status_code=status.HTTP_201_CREATED)
async def create_couple(
    couple: CoupleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new couple."""
    try:
        return CoupleService.create_couple(db, couple, current_user.id)
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=List[CoupleSchema])
async def read_couples(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="Search by names or venue"),
    status: Optional[str] = Query(None, description="Filter by status"),
    wedding_date_from: Optional[datetime] = Query(None, description="Filter by wedding date from"),
    wedding_date_to: Optional[datetime] = Query(None, description="Filter by wedding date to"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all couples for the current celebrant with filtering and pagination."""
    try:
        return CoupleService.get_couples(
            db, current_user.id, skip, limit, search, status, wedding_date_from, wedding_date_to
        )
    except DatabaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{couple_id}", response_model=CoupleSchema)
async def read_couple(
    couple_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific couple."""
    try:
        return CoupleService.get_couple_by_id(db, couple_id, current_user.id)
    except CoupleNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/{couple_id}", response_model=CoupleSchema)
async def update_couple(
    couple_id: int,
    couple_update: CoupleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a couple."""
    try:
        return CoupleService.update_couple(db, couple_id, couple_update, current_user.id)
    except CoupleNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{couple_id}")
async def delete_couple(
    couple_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a couple."""
    try:
        CoupleService.delete_couple(db, couple_id, current_user.id)
        return {"message": "Couple deleted successfully"}
    except CoupleNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/statistics/", response_model=dict)
async def get_couple_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get couple statistics for the current celebrant."""
    try:
        return CoupleService.get_couple_statistics(db, current_user.id)
    except DatabaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/search/", response_model=List[CoupleSchema])
async def search_couples(
    q: str = Query(..., description="Search term"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Search couples by name, venue, or notes."""
    try:
        return CoupleService.search_couples(db, current_user.id, q, limit)
    except DatabaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))