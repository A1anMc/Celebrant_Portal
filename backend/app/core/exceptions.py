"""
Custom exception classes for the Melbourne Celebrant Portal.
Provides consistent error handling across the application.
"""

from fastapi import HTTPException, status
from typing import Optional, Any, Dict


class CelebrantPortalException(HTTPException):
    """Base exception class for all application exceptions."""
    
    def __init__(
        self,
        detail: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class ValidationException(CelebrantPortalException):
    """Raised when data validation fails."""
    
    def __init__(self, detail: str, field: Optional[str] = None):
        if field:
            detail = f"Validation error in field '{field}': {detail}"
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class AuthenticationException(CelebrantPortalException):
    """Raised when authentication fails."""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class AuthorizationException(CelebrantPortalException):
    """Raised when user lacks required permissions."""
    
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class NotFoundException(CelebrantPortalException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource: str, resource_id: Optional[str] = None):
        if resource_id:
            detail = f"{resource} with id {resource_id} not found"
        else:
            detail = f"{resource} not found"
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class ConflictException(CelebrantPortalException):
    """Raised when there's a conflict with existing data."""
    
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)


class RateLimitException(CelebrantPortalException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(detail=detail, status_code=status.HTTP_429_TOO_MANY_REQUESTS)


class DatabaseException(CelebrantPortalException):
    """Raised when database operations fail."""
    
    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(detail=detail, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExternalServiceException(CelebrantPortalException):
    """Raised when external service calls fail."""
    
    def __init__(self, service: str, detail: str = "External service error"):
        detail = f"{service} service error: {detail}"
        super().__init__(detail=detail, status_code=status.HTTP_502_BAD_GATEWAY)


# Specific business exceptions
class UserNotFoundException(NotFoundException):
    """Raised when a user is not found."""
    
    def __init__(self, user_id: Optional[str] = None):
        super().__init__(resource="User", resource_id=user_id)


class CoupleNotFoundException(NotFoundException):
    """Raised when a couple is not found."""
    
    def __init__(self, couple_id: Optional[str] = None):
        super().__init__(resource="Couple", resource_id=couple_id)


class CeremonyNotFoundException(NotFoundException):
    """Raised when a ceremony is not found."""
    
    def __init__(self, ceremony_id: Optional[str] = None):
        super().__init__(resource="Ceremony", resource_id=ceremony_id)


class InvoiceNotFoundException(NotFoundException):
    """Raised when an invoice is not found."""
    
    def __init__(self, invoice_id: Optional[str] = None):
        super().__init__(resource="Invoice", resource_id=invoice_id)


class EmailAlreadyExistsException(ConflictException):
    """Raised when trying to register with an existing email."""
    
    def __init__(self, email: str):
        detail = f"User with email {email} already exists"
        super().__init__(detail=detail)


class InvalidCredentialsException(AuthenticationException):
    """Raised when login credentials are invalid."""
    
    def __init__(self):
        super().__init__(detail="Invalid email or password")


class AccountLockedException(AuthenticationException):
    """Raised when account is locked due to too many failed attempts."""
    
    def __init__(self, lockout_duration: int):
        detail = f"Account is locked for {lockout_duration} minutes due to too many failed login attempts"
        super().__init__(detail=detail)


class TokenExpiredException(AuthenticationException):
    """Raised when JWT token has expired."""
    
    def __init__(self):
        super().__init__(detail="Token has expired")


class InvalidTokenException(AuthenticationException):
    """Raised when JWT token is invalid."""
    
    def __init__(self):
        super().__init__(detail="Invalid token")


class PasswordPolicyException(ValidationException):
    """Raised when password doesn't meet policy requirements."""
    
    def __init__(self, detail: str):
        super().__init__(detail=detail, field="password")


class WeddingDateException(ValidationException):
    """Raised when wedding date is invalid."""
    
    def __init__(self, detail: str):
        super().__init__(detail=detail, field="wedding_date")


class VenueException(ValidationException):
    """Raised when venue information is invalid."""
    
    def __init__(self, detail: str):
        super().__init__(detail=detail, field="venue")


# Error response models
class ErrorResponse:
    """Standard error response model."""
    
    def __init__(
        self,
        error: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        timestamp: Optional[str] = None
    ):
        self.error = error
        self.message = message
        self.details = details or {}
        self.timestamp = timestamp

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.error,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp
        }


class ValidationErrorResponse(ErrorResponse):
    """Validation error response model."""
    
    def __init__(self, field_errors: Dict[str, str]):
        super().__init__(
            error="VALIDATION_ERROR",
            message="Data validation failed",
            details={"field_errors": field_errors}
        )
