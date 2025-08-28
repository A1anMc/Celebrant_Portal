"""
Couple service layer for business logic operations.
Handles all couple-related business operations and data validation.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from datetime import datetime, timedelta

from ..models import Couple, User
from ..schemas import CoupleCreate, CoupleUpdate
from ..core.exceptions import (
    CoupleNotFoundException,
    ValidationException,
    AuthorizationException,
    DatabaseException
)


class CoupleService:
    """Service class for couple management operations."""
    
    @staticmethod
    def get_couples(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[str] = None,
        wedding_date_from: Optional[datetime] = None,
        wedding_date_to: Optional[datetime] = None
    ) -> List[Couple]:
        """
        Get couples for a specific celebrant with filtering and pagination.
        
        Args:
            db: Database session
            user_id: ID of the celebrant
            skip: Number of records to skip
            limit: Maximum number of records to return
            search: Search term for names or venue
            status: Filter by couple status
            wedding_date_from: Filter by wedding date from
            wedding_date_to: Filter by wedding date to
            
        Returns:
            List of couples matching the criteria
        """
        try:
            query = db.query(Couple).filter(Couple.celebrant_id == user_id)
            
            # Apply search filter
            if search:
                search_term = f"%{search}%"
                query = query.filter(
                    or_(
                        Couple.partner1_name.ilike(search_term),
                        Couple.partner2_name.ilike(search_term),
                        Couple.venue.ilike(search_term),
                        Couple.notes.ilike(search_term)
                    )
                )
            
            # Apply status filter
            if status:
                query = query.filter(Couple.status == status)
            
            # Apply date range filter
            if wedding_date_from:
                query = query.filter(Couple.wedding_date >= wedding_date_from)
            if wedding_date_to:
                query = query.filter(Couple.wedding_date <= wedding_date_to)
            
            # Apply pagination and ordering
            couples = query.order_by(desc(Couple.created_at)).offset(skip).limit(limit).all()
            
            return couples
            
        except Exception as e:
            raise DatabaseException(f"Failed to retrieve couples: {str(e)}")
    
    @staticmethod
    def get_couple_by_id(db: Session, couple_id: int, user_id: int) -> Couple:
        """
        Get a specific couple by ID, ensuring it belongs to the user.
        
        Args:
            db: Database session
            couple_id: ID of the couple
            user_id: ID of the celebrant
            
        Returns:
            Couple object
            
        Raises:
            CoupleNotFoundException: If couple not found or doesn't belong to user
        """
        try:
            couple = db.query(Couple).filter(
                and_(
                    Couple.id == couple_id,
                    Couple.celebrant_id == user_id
                )
            ).first()
            
            if not couple:
                raise CoupleNotFoundException(str(couple_id))
            
            return couple
            
        except CoupleNotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(f"Failed to retrieve couple: {str(e)}")
    
    @staticmethod
    def create_couple(db: Session, couple_data: CoupleCreate, user_id: int) -> Couple:
        """
        Create a new couple for a celebrant.
        
        Args:
            db: Database session
            couple_data: Couple creation data
            user_id: ID of the celebrant
            
        Returns:
            Created couple object
            
        Raises:
            ValidationException: If data validation fails
        """
        try:
            # Validate wedding date
            if couple_data.wedding_date:
                if couple_data.wedding_date < datetime.now():
                    raise ValidationException(
                        "Wedding date cannot be in the past",
                        field="wedding_date"
                    )
            
            # Validate email addresses
            if couple_data.partner1_email == couple_data.partner2_email:
                raise ValidationException(
                    "Partner email addresses must be different",
                    field="partner2_email"
                )
            
            # Create couple object
            couple = Couple(
                **couple_data.model_dump(),
                celebrant_id=user_id
            )
            
            db.add(couple)
            db.commit()
            db.refresh(couple)
            
            return couple
            
        except ValidationException:
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseException(f"Failed to create couple: {str(e)}")
    
    @staticmethod
    def update_couple(
        db: Session,
        couple_id: int,
        couple_data: CoupleUpdate,
        user_id: int
    ) -> Couple:
        """
        Update an existing couple.
        
        Args:
            db: Database session
            couple_id: ID of the couple
            couple_data: Couple update data
            user_id: ID of the celebrant
            
        Returns:
            Updated couple object
            
        Raises:
            CoupleNotFoundException: If couple not found
            ValidationException: If data validation fails
        """
        try:
            # Get existing couple
            couple = CoupleService.get_couple_by_id(db, couple_id, user_id)
            
            # Validate wedding date if provided
            if couple_data.wedding_date:
                if couple_data.wedding_date < datetime.now():
                    raise ValidationException(
                        "Wedding date cannot be in the past",
                        field="wedding_date"
                    )
            
            # Validate email addresses if provided
            if couple_data.partner1_email and couple_data.partner2_email:
                if couple_data.partner1_email == couple_data.partner2_email:
                    raise ValidationException(
                        "Partner email addresses must be different",
                        field="partner2_email"
                    )
            
            # Update couple fields
            update_data = couple_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(couple, field, value)
            
            db.commit()
            db.refresh(couple)
            
            return couple
            
        except (CoupleNotFoundException, ValidationException):
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseException(f"Failed to update couple: {str(e)}")
    
    @staticmethod
    def delete_couple(db: Session, couple_id: int, user_id: int) -> bool:
        """
        Delete a couple.
        
        Args:
            db: Database session
            couple_id: ID of the couple
            user_id: ID of the celebrant
            
        Returns:
            True if deletion was successful
            
        Raises:
            CoupleNotFoundException: If couple not found
        """
        try:
            # Get existing couple
            couple = CoupleService.get_couple_by_id(db, couple_id, user_id)
            
            db.delete(couple)
            db.commit()
            
            return True
            
        except CoupleNotFoundException:
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseException(f"Failed to delete couple: {str(e)}")
    
    @staticmethod
    def get_couple_statistics(db: Session, user_id: int) -> Dict[str, Any]:
        """
        Get statistics for a celebrant's couples.
        
        Args:
            db: Database session
            user_id: ID of the celebrant
            
        Returns:
            Dictionary with couple statistics
        """
        try:
            total_couples = db.query(Couple).filter(Couple.celebrant_id == user_id).count()
            
            # Count by status
            inquiries = db.query(Couple).filter(
                and_(
                    Couple.celebrant_id == user_id,
                    Couple.status == "Inquiry"
                )
            ).count()
            
            booked = db.query(Couple).filter(
                and_(
                    Couple.celebrant_id == user_id,
                    Couple.status == "Booked"
                )
            ).count()
            
            completed = db.query(Couple).filter(
                and_(
                    Couple.celebrant_id == user_id,
                    Couple.status == "Completed"
                )
            ).count()
            
            # Upcoming weddings (next 30 days)
            thirty_days_from_now = datetime.now() + timedelta(days=30)
            upcoming = db.query(Couple).filter(
                and_(
                    Couple.celebrant_id == user_id,
                    Couple.wedding_date >= datetime.now(),
                    Couple.wedding_date <= thirty_days_from_now,
                    Couple.status == "Booked"
                )
            ).count()
            
            return {
                "total_couples": total_couples,
                "inquiries": inquiries,
                "booked": booked,
                "completed": completed,
                "upcoming_weddings": upcoming
            }
            
        except Exception as e:
            raise DatabaseException(f"Failed to retrieve couple statistics: {str(e)}")
    
    @staticmethod
    def search_couples(
        db: Session,
        user_id: int,
        search_term: str,
        limit: int = 10
    ) -> List[Couple]:
        """
        Search couples by name, venue, or notes.
        
        Args:
            db: Database session
            user_id: ID of the celebrant
            search_term: Search term
            limit: Maximum number of results
            
        Returns:
            List of matching couples
        """
        try:
            search_pattern = f"%{search_term}%"
            
            couples = db.query(Couple).filter(
                and_(
                    Couple.celebrant_id == user_id,
                    or_(
                        Couple.partner1_name.ilike(search_pattern),
                        Couple.partner2_name.ilike(search_pattern),
                        Couple.venue.ilike(search_pattern),
                        Couple.notes.ilike(search_pattern)
                    )
                )
            ).order_by(desc(Couple.created_at)).limit(limit).all()
            
            return couples
            
        except Exception as e:
            raise DatabaseException(f"Failed to search couples: {str(e)}")
