"""
Production configuration for Melbourne Celebrant Portal
"""
from app.core.config import Settings

class ProductionSettings(Settings):
    """Production-specific settings."""
    
    # Environment
    environment: str = "production"
    debug: bool = False
    
    # Security
    session_cookie_secure: bool = True
    session_cookie_httponly: bool = True
    session_cookie_samesite: str = "Strict"
    
    # Database
    # DATABASE_URL should be set via environment variable
    
    # Logging
    log_level: str = "INFO"
    
    # Rate Limiting (stricter in production)
    rate_limit_calls: int = 50
    rate_limit_window: int = 60
    
    # CORS (restrict to actual domains)
    # ALLOWED_ORIGINS should be set via environment variable
    
    class Config:
        env_file = ".env.production"
        extra = "ignore"

# Production settings instance
production_settings = ProductionSettings()
