"""
User service layer for business logic operations.
Handles all user-related business operations and data validation.
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime, timedelta

from ..models import User, FailedLoginAttempt
from ..schemas import UserCreate, UserUpdate
from ..core.auth import get_password_hash, verify_password
from ..core.exceptions import (
    UserNotFoundException,
    EmailAlreadyExistsException,
    InvalidCredentialsException,
    AccountLockedException,
    PasswordPolicyException,
    ValidationException,
    DatabaseException
)
from ..core.config import settings


class UserService:
    """Service class for user management operations."""
    
    @staticmethod
    def validate_password(password: str) -> bool:
        """
        Validate password against security policy.
        
        Args:
            password: Password to validate
            
        Returns:
            True if password meets requirements
            
        Raises:
            PasswordPolicyException: If password doesn't meet requirements
        """
        if len(password) < settings.min_password_length:
            raise PasswordPolicyException(
                f"Password must be at least {settings.min_password_length} characters long"
            )
        
        if settings.password_require_uppercase and not any(c.isupper() for c in password):
            raise PasswordPolicyException("Password must contain at least one uppercase letter")
        
        if settings.password_require_lowercase and not any(c.islower() for c in password):
            raise PasswordPolicyException("Password must contain at least one lowercase letter")
        
        if settings.password_require_numbers and not any(c.isdigit() for c in password):
            raise PasswordPolicyException("Password must contain at least one number")
        
        if settings.password_require_special and not any(c in "!@#$%^&*(),.?\":{}|<>" for c in password):
            raise PasswordPolicyException("Password must contain at least one special character")
        
        return True
    
    @staticmethod
    def check_account_lockout(db: Session, email: str) -> Optional[timedelta]:
        """
        Check if account is locked and return remaining lockout time.
        
        Args:
            db: Database session
            email: User email
            
        Returns:
            Remaining lockout time or None if not locked
        """
        try:
            # Count recent failed attempts
            recent_attempts = db.query(FailedLoginAttempt).filter(
                and_(
                    FailedLoginAttempt.email == email,
                    FailedLoginAttempt.timestamp > datetime.utcnow() - timedelta(minutes=settings.lockout_duration_minutes)
                )
            ).count()
            
            if recent_attempts >= settings.max_login_attempts:
                # Get the latest failed attempt
                latest_attempt = db.query(FailedLoginAttempt).filter(
                    FailedLoginAttempt.email == email
                ).order_by(FailedLoginAttempt.timestamp.desc()).first()
                
                if latest_attempt:
                    lockout_end = latest_attempt.timestamp + timedelta(minutes=settings.lockout_duration_minutes)
                    if lockout_end > datetime.utcnow():
                        return lockout_end - datetime.utcnow()
            
            return None
            
        except Exception as e:
            raise DatabaseException(f"Failed to check account lockout: {str(e)}")
    
    @staticmethod
    def record_failed_attempt(db: Session, email: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> None:
        """
        Record a failed login attempt.
        
        Args:
            db: Database session
            email: User email
            ip_address: IP address of the attempt
            user_agent: User agent string
        """
        try:
            failed_attempt = FailedLoginAttempt(
                email=email,
                ip_address=ip_address,
                user_agent=user_agent
            )
            db.add(failed_attempt)
            db.commit()
            
        except Exception as e:
            db.rollback()
            raise DatabaseException(f"Failed to record failed attempt: {str(e)}")
    
    @staticmethod
    def clear_failed_attempts(db: Session, email: str) -> None:
        """
        Clear failed login attempts for a user.
        
        Args:
            db: Database session
            email: User email
        """
        try:
            db.query(FailedLoginAttempt).filter(FailedLoginAttempt.email == email).delete()
            db.commit()
            
        except Exception as e:
            db.rollback()
            raise DatabaseException(f"Failed to clear failed attempts: {str(e)}")
    
    @staticmethod
    async def create_user(db: Session, user_data: UserCreate) -> User:
        """
        Create a new user account.
        
        Args:
            db: Database session
            user_data: User creation data
            
        Returns:
            Created user object
            
        Raises:
            EmailAlreadyExistsException: If email already exists
            PasswordPolicyException: If password doesn't meet requirements
        """
        try:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == user_data.email).first()
            if existing_user:
                raise EmailAlreadyExistsException(user_data.email)
            
            # Validate password
            UserService.validate_password(user_data.password)
            
            # Hash password
            hashed_password = get_password_hash(user_data.password)
            
            # Create user
            user = User(
                email=user_data.email,
                hashed_password=hashed_password,
                full_name=user_data.full_name
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            return user
            
        except (EmailAlreadyExistsException, PasswordPolicyException):
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseException(f"Failed to create user: {str(e)}")
    
    @staticmethod
    async def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            db: Database session
            email: User email
            
        Returns:
            User object or None if not found
        """
        try:
            return db.query(User).filter(User.email == email).first()
            
        except Exception as e:
            raise DatabaseException(f"Failed to retrieve user: {str(e)}")
    
    @staticmethod
    async def get_user_by_id(db: Session, user_id: int) -> User:
        """
        Get user by ID.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            User object
            
        Raises:
            UserNotFoundException: If user not found
        """
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                raise UserNotFoundException(str(user_id))
            
            return user
            
        except UserNotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(f"Failed to retrieve user: {str(e)}")
    
    @staticmethod
    async def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
        """
        Update user information.
        
        Args:
            db: Database session
            user_id: User ID
            user_data: User update data
            
        Returns:
            Updated user object
            
        Raises:
            UserNotFoundException: If user not found
            EmailAlreadyExistsException: If new email already exists
        """
        try:
            # Get existing user
            user = await UserService.get_user_by_id(db, user_id)
            
            # Check if new email already exists (if email is being updated)
            if user_data.email and user_data.email != user.email:
                existing_user = db.query(User).filter(User.email == user_data.email).first()
                if existing_user:
                    raise EmailAlreadyExistsException(user_data.email)
            
            # Update user fields
            update_data = user_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(user, field, value)
            
            db.commit()
            db.refresh(user)
            
            return user
            
        except (UserNotFoundException, EmailAlreadyExistsException):
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseException(f"Failed to update user: {str(e)}")
    
    @staticmethod
    async def authenticate_user(db: Session, email: str, password: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> User:
        """
        Authenticate a user with email and password.
        
        Args:
            db: Database session
            email: User email
            password: User password
            ip_address: IP address for security logging
            user_agent: User agent for security logging
            
        Returns:
            Authenticated user object
            
        Raises:
            InvalidCredentialsException: If credentials are invalid
            AccountLockedException: If account is locked
        """
        try:
            # Check for account lockout
            lockout_time = UserService.check_account_lockout(db, email)
            if lockout_time:
                raise AccountLockedException(int(lockout_time.total_seconds() / 60))
            
            # Get user by email
            user = await UserService.get_user_by_email(db, email)
            if not user:
                UserService.record_failed_attempt(db, email, ip_address, user_agent)
                raise InvalidCredentialsException()
            
            # Verify password
            if not verify_password(password, user.hashed_password):
                UserService.record_failed_attempt(db, email, ip_address, user_agent)
                raise InvalidCredentialsException()
            
            # Check if user is active
            if not user.is_active:
                raise InvalidCredentialsException()
            
            # Clear failed attempts on successful login
            UserService.clear_failed_attempts(db, email)
            
            return user
            
        except (InvalidCredentialsException, AccountLockedException):
            raise
        except Exception as e:
            raise DatabaseException(f"Failed to authenticate user: {str(e)}")
    
    @staticmethod
    async def change_password(db: Session, user_id: int, current_password: str, new_password: str) -> bool:
        """
        Change user password.
        
        Args:
            db: Database session
            user_id: User ID
            current_password: Current password
            new_password: New password
            
        Returns:
            True if password was changed successfully
            
        Raises:
            UserNotFoundException: If user not found
            InvalidCredentialsException: If current password is incorrect
            PasswordPolicyException: If new password doesn't meet requirements
        """
        try:
            # Get user
            user = await UserService.get_user_by_id(db, user_id)
            
            # Verify current password
            if not verify_password(current_password, user.hashed_password):
                raise InvalidCredentialsException()
            
            # Validate new password
            UserService.validate_password(new_password)
            
            # Hash new password
            hashed_password = get_password_hash(new_password)
            
            # Update password
            user.hashed_password = hashed_password
            db.commit()
            
            return True
            
        except (UserNotFoundException, InvalidCredentialsException, PasswordPolicyException):
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseException(f"Failed to change password: {str(e)}")
    
    @staticmethod
    async def deactivate_user(db: Session, user_id: int) -> bool:
        """
        Deactivate a user account.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            True if user was deactivated successfully
            
        Raises:
            UserNotFoundException: If user not found
        """
        try:
            # Get user
            user = await UserService.get_user_by_id(db, user_id)
            
            # Deactivate user
            user.is_active = False
            db.commit()
            
            return True
            
        except UserNotFoundException:
            raise
        except Exception as e:
            db.rollback()
            raise DatabaseException(f"Failed to deactivate user: {str(e)}")
    
    @staticmethod
    async def get_user_statistics(db: Session, user_id: int) -> Dict[str, Any]:
        """
        Get user statistics and activity information.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Dictionary with user statistics
        """
        try:
            user = await UserService.get_user_by_id(db, user_id)
            
            # Count couples
            couple_count = db.query(user.couples).count()
            
            # Count recent failed login attempts
            recent_failed_attempts = db.query(FailedLoginAttempt).filter(
                and_(
                    FailedLoginAttempt.email == user.email,
                    FailedLoginAttempt.timestamp > datetime.utcnow() - timedelta(days=30)
                )
            ).count()
            
            return {
                "user_id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "is_active": user.is_active,
                "created_at": user.created_at,
                "updated_at": user.updated_at,
                "couple_count": couple_count,
                "recent_failed_attempts": recent_failed_attempts
            }
            
        except UserNotFoundException:
            raise
        except Exception as e:
            raise DatabaseException(f"Failed to retrieve user statistics: {str(e)}")
