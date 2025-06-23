"""
Rate limiting configuration for the Celebrant Portal
"""
from flask import request, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import current_user
import logging

logger = logging.getLogger(__name__)


def get_user_id():
    """Get user ID for rate limiting key."""
    if hasattr(g, 'current_user') and current_user.is_authenticated:
        return f"user:{current_user.id}"
    return get_remote_address()


def get_organization_id():
    """Get organization ID for rate limiting key."""
    if hasattr(g, 'current_user') and current_user.is_authenticated:
        return f"org:{current_user.organization_id}"
    return get_remote_address()


def init_limiter(app):
    """Initialize rate limiter with Flask app."""
    
    # Configure rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_user_id,
        default_limits=["1000 per hour", "100 per minute"],
        storage_uri="memory://",  # Use Redis in production
        headers_enabled=True,
        retry_after="http-date"
    )
    
    # Custom rate limit exceeded handler
    @limiter.request_filter
    def ip_whitelist():
        """Whitelist certain IPs from rate limiting."""
        # Add your trusted IPs here
        trusted_ips = ['127.0.0.1', '::1']
        return request.remote_addr in trusted_ips
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        """Handle rate limit exceeded errors."""
        logger.warning(f"Rate limit exceeded for {request.remote_addr} on {request.endpoint}")
        return {
            'error': 'Rate limit exceeded',
            'message': 'Too many requests. Please try again later.',
            'retry_after': error.retry_after
        }, 429
    
    return limiter


# Rate limit decorators for different endpoints
def auth_rate_limit():
    """Rate limit for authentication endpoints."""
    return "5 per minute"


def api_rate_limit():
    """Rate limit for API endpoints."""
    return "60 per minute"


def upload_rate_limit():
    """Rate limit for file upload endpoints."""
    return "10 per minute"


def email_rate_limit():
    """Rate limit for email-related endpoints."""
    return "20 per minute"


def search_rate_limit():
    """Rate limit for search endpoints."""
    return "30 per minute"


def export_rate_limit():
    """Rate limit for export endpoints."""
    return "10 per minute"


# Organization-based rate limits
def org_api_rate_limit():
    """Organization-based API rate limit."""
    return "500 per hour"


def org_upload_rate_limit():
    """Organization-based upload rate limit."""
    return "50 per hour"


# Premium tier rate limits
def premium_api_rate_limit():
    """Premium tier API rate limit."""
    if hasattr(g, 'current_user') and current_user.is_authenticated:
        if current_user.organization.subscription_plan == 'premium':
            return "2000 per hour"
    return "500 per hour" 