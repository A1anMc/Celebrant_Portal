from pydantic_settings import BaseSettings
from typing import Optional, List
import os
import secrets
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_allowed_origins() -> List[str]:
    """Parse ALLOWED_ORIGINS environment variable safely."""
    env_origins = os.getenv("ALLOWED_ORIGINS")
    if env_origins:
        return [origin.strip() for origin in env_origins.split(",") if origin.strip()]
    
    # Fallback to defaults
    return [
        "http://localhost:3000",
        "https://celebrant-portal-ah8ssgciz-alans-projects-baf4c067.vercel.app"
    ]

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./celebrant_portal.db")
    
    # Validate DATABASE_URL format
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # If DATABASE_URL is malformed or empty, fallback to SQLite
        if not self.database_url or self.database_url == "postgresql://username:password@host:port/database_name":
            self.database_url = "sqlite:///./celebrant_portal.db"
            print("Warning: Using SQLite database as fallback")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Password Policy
    min_password_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_numbers: bool = True
    password_require_special: bool = True
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15
    
    # Rate Limiting
    rate_limit_calls: int = 100
    rate_limit_window: int = 60  # seconds
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Render specific
    port: int = int(os.getenv("PORT", "8000"))
    host: str = os.getenv("HOST", "0.0.0.0")
    
    # Security Headers
    csrf_token_secret: str = os.getenv("CSRF_TOKEN_SECRET", secrets.token_urlsafe(32))
    session_cookie_secure: bool = True
    session_cookie_httponly: bool = True
    session_cookie_samesite: str = "Lax"
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings() 