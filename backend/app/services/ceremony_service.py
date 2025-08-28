"""
Ceremony service layer for business logic operations.
Handles all ceremony-related business operations and data validation.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime

from ..models import Ceremony, Couple
from ..schemas import CeremonyCreate, CeremonyUpdate
from ..core.exceptions import (
    CeremonyNotFoundException,
    CoupleNotFoundException,
    ValidationException,
    DatabaseException
)


class CeremonyService:
    """Service class for ceremony management operations."""
    
    @staticmethod
    async def get_ceremonies_by_couple(
        db: Session,
        couple_id: int,
        user_id: int
    ) -> List[Ceremony]:
        """
        Get all ceremonies for a specific couple.
        
        Args:
            db: Database session
            couple_id: ID of the couple
            user_id: ID of the celebrant (for authorization)
            
        Returns:
            List of ceremonies for the couple
            
        Raises:
            CoupleNotFoundException: If couple not found or doesn't belong to user
        """
        try:
            # Verify couple belongs to user
            couple = db.query(Couple).filter(
                and_(
                    Couple.id == couple_id,
                    Couple.celebrant_id == user_id
                )
            ).first()
            
            if not couple:
                raise CoupleNotFoundException(str(couple_id))
            
            # Get ceremonies
            ceremonies = db.query(Ceremony).filter(
                Ceremony.couple_id == couple_id
            ).order_by(desc(Ceremony.created_at)).all()
            
            return ceremonies
            
        except CoupleNotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(f"Failed to retrieve ceremonies: {str(e)}")
    
    @staticmethod
    async def get_ceremony_by_id(
        db: Session,
        ceremony_id: int,
        user_id: int
    ) -> Ceremony:
        """
        Get a specific ceremony by ID.
        
        Args:
            db: Database session
            ceremony_id: ID of the ceremony
            user_id: ID of the celebrant (for authorization)
            
        Returns:
            Ceremony object
            
        Raises:
            CeremonyNotFoundException: If ceremony not found
        """
        try:
            # Get ceremony with couple relationship
            ceremony = db.query(Ceremony).join(Couple).filter(
                and_(
                    Ceremony.id == ceremony_id,
                    Couple.celebrant_id == user_id
                )
            ).first()
            
            if not ceremony:
                raise CeremonyNotFoundException(str(ceremony_id))
            
            return ceremony
            
        except CeremonyNotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(f"Failed to retrieve ceremony: {str(e)}")
    
    @staticmethod
    async def create_ceremony(
        db: Session,
        ceremony_data: CeremonyCreate,
        user_id: int
    ) -> Ceremony:
        """
        Create a new ceremony for a couple.
        
        Args:
            db: Database session
            ceremony_data: Ceremony creation data
            user_id: ID of the celebrant (for authorization)
            
        Returns:
            Created ceremony object
            
        Raises:
            CoupleNotFoundException: If couple not found or doesn't belong to user
            ValidationException: If data validation fails
        """
        try:
            # Verify couple belongs to user
            couple = db.query(Couple).filter(
                and_(
                    Couple.id == ceremony_data.couple_id,
                    Couple.celebrant_id == user_id
                )
            ).first()
            
            if not couple:
                raise CoupleNotFoundException(str(ceremony_data.couple_id))
            
            # Validate ceremony data
            if ceremony_data.ceremony_script and len(ceremony_data.ceremony_script.strip()) < 10:
                raise ValidationException(
                    "Ceremony script must be at least 10 characters long",
                    field="ceremony_script"
                )
            
            # Create ceremony
            ceremony = Ceremony(**ceremony_data.dict())
            
            db.add(ceremony)
            db.commit()
            db.refresh(ceremony)
            
            return ceremony
            
        except (CoupleNotFoundException, ValidationException):
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseException(f"Failed to create ceremony: {str(e)}")
    
    @staticmethod
    async def update_ceremony(
        db: Session,
        ceremony_id: int,
        ceremony_data: CeremonyUpdate,
        user_id: int
    ) -> Ceremony:
        """
        Update an existing ceremony.
        
        Args:
            db: Database session
            ceremony_id: ID of the ceremony
            ceremony_data: Ceremony update data
            user_id: ID of the celebrant (for authorization)
            
        Returns:
            Updated ceremony object
            
        Raises:
            CeremonyNotFoundException: If ceremony not found
            ValidationException: If data validation fails
        """
        try:
            # Get existing ceremony
            ceremony = await CeremonyService.get_ceremony_by_id(db, ceremony_id, user_id)
            
            # Validate ceremony script if provided
            if ceremony_data.ceremony_script:
                if len(ceremony_data.ceremony_script.strip()) < 10:
                    raise ValidationException(
                        "Ceremony script must be at least 10 characters long",
                        field="ceremony_script"
                    )
            
            # Update ceremony fields
            update_data = ceremony_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(ceremony, field, value)
            
            db.commit()
            db.refresh(ceremony)
            
            return ceremony
            
        except (CeremonyNotFoundException, ValidationException):
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseException(f"Failed to update ceremony: {str(e)}")
    
    @staticmethod
    async def delete_ceremony(
        db: Session,
        ceremony_id: int,
        user_id: int
    ) -> bool:
        """
        Delete a ceremony.
        
        Args:
            db: Database session
            ceremony_id: ID of the ceremony
            user_id: ID of the celebrant (for authorization)
            
        Returns:
            True if deletion was successful
            
        Raises:
            CeremonyNotFoundException: If ceremony not found
        """
        try:
            # Get existing ceremony
            ceremony = await CeremonyService.get_ceremony_by_id(db, ceremony_id, user_id)
            
            db.delete(ceremony)
            db.commit()
            
            return True
            
        except CeremonyNotFoundException:
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseException(f"Failed to delete ceremony: {str(e)}")
    
    @staticmethod
    async def get_ceremony_templates(
        db: Session,
        user_id: int,
        template_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get ceremony templates for a celebrant.
        
        Args:
            db: Database session
            user_id: ID of the celebrant
            template_type: Type of template to filter by
            
        Returns:
            List of ceremony templates
        """
        try:
            # This would typically query a templates table
            # For now, return some default templates
            templates = [
                {
                    "id": 1,
                    "name": "Traditional Wedding Ceremony",
                    "type": "wedding",
                    "description": "A traditional wedding ceremony with standard vows",
                    "content": "Dearly beloved, we are gathered here today..."
                },
                {
                    "id": 2,
                    "name": "Modern Wedding Ceremony",
                    "type": "wedding",
                    "description": "A modern, personalized wedding ceremony",
                    "content": "Welcome everyone to this celebration of love..."
                },
                {
                    "id": 3,
                    "name": "Commitment Ceremony",
                    "type": "commitment",
                    "description": "A commitment ceremony for couples",
                    "content": "Today we celebrate the commitment between..."
                }
            ]
            
            if template_type:
                templates = [t for t in templates if t["type"] == template_type]
            
            return templates
            
        except Exception as e:
            raise DatabaseException(f"Failed to retrieve ceremony templates: {str(e)}")
    
    @staticmethod
    async def generate_ceremony_script(
        db: Session,
        ceremony_id: int,
        user_id: int,
        template_id: Optional[int] = None
    ) -> str:
        """
        Generate a ceremony script based on template and couple information.
        
        Args:
            db: Database session
            ceremony_id: ID of the ceremony
            user_id: ID of the celebrant
            template_id: ID of the template to use
            
        Returns:
            Generated ceremony script
            
        Raises:
            CeremonyNotFoundException: If ceremony not found
        """
        try:
            # Get ceremony with couple information
            ceremony = await CeremonyService.get_ceremony_by_id(db, ceremony_id, user_id)
            
            # Get couple information
            couple = ceremony.couple
            
            # Get template if specified
            template_content = ""
            if template_id:
                templates = await CeremonyService.get_ceremony_templates(db, user_id)
                template = next((t for t in templates if t["id"] == template_id), None)
                if template:
                    template_content = template["content"]
            
            # Generate personalized script
            script = f"""
# Wedding Ceremony Script
# {couple.partner1_name} & {couple.partner2_name}
# {couple.wedding_date.strftime('%B %d, %Y') if couple.wedding_date else 'Date TBD'}
# Venue: {couple.venue or 'Venue TBD'}

{template_content}

## Personal Vows

### {couple.partner1_name}'s Vows:
{ceremony.vows_partner1 or '[Personal vows to be written]'}

### {couple.partner2_name}'s Vows:
{ceremony.vows_partner2 or '[Personal vows to be written]'}

## Ring Exchange
{ceremony.ring_exchange or '[Ring exchange ceremony to be written]'}

## Special Readings
{ceremony.special_readings or '[Special readings to be selected]'}

## Music Notes
{ceremony.music_notes or '[Music selections to be determined]'}

---
Generated by Melbourne Celebrant Portal
"""
            
            return script.strip()
            
        except CeremonyNotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(f"Failed to generate ceremony script: {str(e)}")
    
    @staticmethod
    async def get_ceremony_statistics(
        db: Session,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Get ceremony statistics for a celebrant.
        
        Args:
            db: Database session
            user_id: ID of the celebrant
            
        Returns:
            Dictionary with ceremony statistics
        """
        try:
            # Count total ceremonies
            total_ceremonies = db.query(Ceremony).join(Couple).filter(
                Couple.celebrant_id == user_id
            ).count()
            
            # Count ceremonies with scripts
            ceremonies_with_scripts = db.query(Ceremony).join(Couple).filter(
                and_(
                    Couple.celebrant_id == user_id,
                    Ceremony.ceremony_script.isnot(None),
                    Ceremony.ceremony_script != ""
                )
            ).count()
            
            # Count ceremonies with vows
            ceremonies_with_vows = db.query(Ceremony).join(Couple).filter(
                and_(
                    Couple.celebrant_id == user_id,
                    Ceremony.vows_partner1.isnot(None),
                    Ceremony.vows_partner1 != ""
                )
            ).count()
            
            return {
                "total_ceremonies": total_ceremonies,
                "ceremonies_with_scripts": ceremonies_with_scripts,
                "ceremonies_with_vows": ceremonies_with_vows,
                "completion_rate": (ceremonies_with_scripts / total_ceremonies * 100) if total_ceremonies > 0 else 0
            }
            
        except Exception as e:
            raise DatabaseException(f"Failed to retrieve ceremony statistics: {str(e)}")
