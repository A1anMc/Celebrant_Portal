"""
Ceremonies API router.
Handles all ceremony-related endpoints with proper error handling.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...models import User
from ...schemas import CeremonyCreate, CeremonyUpdate, Ceremony as CeremonySchema
from ...core.auth import get_current_active_user
from ...services.ceremony_service import CeremonyService
from ...core.exceptions import (
    CeremonyNotFoundException,
    CoupleNotFoundException,
    ValidationException,
    DatabaseException
)

router = APIRouter(prefix="/ceremonies", tags=["ceremonies"])

@router.post("/", response_model=CeremonySchema)
async def create_ceremony(
    ceremony: CeremonyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new ceremony for a couple."""
    try:
        return await CeremonyService.create_ceremony(db, ceremony, current_user.id)
    except CoupleNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/couple/{couple_id}", response_model=List[CeremonySchema])
async def get_ceremonies_by_couple(
    couple_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all ceremonies for a specific couple."""
    try:
        return await CeremonyService.get_ceremonies_by_couple(db, couple_id, current_user.id)
    except CoupleNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{ceremony_id}", response_model=CeremonySchema)
async def get_ceremony(
    ceremony_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific ceremony by ID."""
    try:
        return await CeremonyService.get_ceremony_by_id(db, ceremony_id, current_user.id)
    except CeremonyNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/{ceremony_id}", response_model=CeremonySchema)
async def update_ceremony(
    ceremony_id: int,
    ceremony_update: CeremonyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update an existing ceremony."""
    try:
        return await CeremonyService.update_ceremony(db, ceremony_id, ceremony_update, current_user.id)
    except CeremonyNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{ceremony_id}")
async def delete_ceremony(
    ceremony_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a ceremony."""
    try:
        await CeremonyService.delete_ceremony(db, ceremony_id, current_user.id)
        return {"message": "Ceremony deleted successfully"}
    except CeremonyNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/templates/", response_model=List[dict])
async def get_ceremony_templates(
    template_type: Optional[str] = Query(None, description="Filter by template type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get ceremony templates."""
    try:
        return await CeremonyService.get_ceremony_templates(db, current_user.id, template_type)
    except DatabaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{ceremony_id}/script", response_model=str)
async def generate_ceremony_script(
    ceremony_id: int,
    template_id: Optional[int] = Query(None, description="Template ID to use"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Generate a ceremony script."""
    try:
        return await CeremonyService.generate_ceremony_script(db, ceremony_id, current_user.id, template_id)
    except CeremonyNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DatabaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/statistics/", response_model=dict)
async def get_ceremony_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get ceremony statistics for the current celebrant."""
    try:
        return await CeremonyService.get_ceremony_statistics(db, current_user.id)
    except DatabaseException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
