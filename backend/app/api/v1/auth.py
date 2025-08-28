from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...models import User, FailedLoginAttempt
from ...schemas import UserCreate, User, Token
from ...core.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_active_user,
    verify_password,
    get_current_user
)
from ...core.config import settings
import re
from typing import Optional
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError

router = APIRouter(prefix="/auth", tags=["authentication"])

def validate_password(password: str) -> bool:
    """Validate password against security policy."""
    if len(password) < settings.min_password_length:
        return False
    
    if settings.password_require_uppercase and not re.search(r'[A-Z]', password):
        return False
    
    if settings.password_require_lowercase and not re.search(r'[a-z]', password):
        return False
    
    if settings.password_require_numbers and not re.search(r'\d', password):
        return False
    
    if settings.password_require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    
    return True

def check_account_lockout(db: Session, email: str) -> Optional[timedelta]:
    """Check if account is locked and return remaining lockout time if it is."""
    failed_attempts = db.query(FailedLoginAttempt).filter(
        FailedLoginAttempt.email == email,
        FailedLoginAttempt.timestamp > datetime.utcnow() - timedelta(minutes=settings.lockout_duration_minutes)
    ).count()
    
    if failed_attempts >= settings.max_login_attempts:
        latest_attempt = db.query(FailedLoginAttempt).filter(
            FailedLoginAttempt.email == email
        ).order_by(FailedLoginAttempt.timestamp.desc()).first()
        
        if latest_attempt:
            lockout_end = latest_attempt.timestamp + timedelta(minutes=settings.lockout_duration_minutes)
            if lockout_end > datetime.utcnow():
                return lockout_end - datetime.utcnow()
    
    return None

def record_failed_attempt(db: Session, email: str):
    """Record a failed login attempt."""
    failed_attempt = FailedLoginAttempt(email=email)
    db.add(failed_attempt)
    db.commit()

def clear_failed_attempts(db: Session, email: str):
    """Clear failed login attempts for a user."""
    db.query(FailedLoginAttempt).filter(FailedLoginAttempt.email == email).delete()
    db.commit()

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    # Validate password
    if not validate_password(user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password does not meet security requirements"
        )
    
    # Check if user exists
    from app.models import User as UserModel
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login user and return access token."""
    # Check for account lockout
    lockout_time = check_account_lockout(db, form_data.username)
    if lockout_time:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is locked. Try again in {int(lockout_time.total_seconds() / 60)} minutes"
        )
    
    # Authenticate user
    from app.models import User as UserModel
    user = db.query(UserModel).filter(UserModel.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        record_failed_attempt(db, form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Clear failed attempts on successful login
    clear_failed_attempts(db, form_data.username)
    
    # Generate access token
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    
    # Generate refresh token
    refresh_token = create_access_token(
        data={"sub": user.email, "refresh": True},
        expires_delta=timedelta(days=settings.refresh_token_expire_days)
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_user),
    csrf_protect: CsrfProtect = Depends()
):
    """Refresh access token."""
    access_token = create_access_token(
        data={"sub": current_user.email},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    csrf_protect: CsrfProtect = Depends()
):
    """Logout user."""
    # In a more complete implementation, you would add the token to a blacklist here
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=User)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user

@router.get("/verify")
def verify_token(current_user: User = Depends(get_current_active_user)):
    """Verify if token is valid."""
    return {"valid": True, "user_id": current_user.id} 