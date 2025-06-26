import os
from typing import List, Optional


class Settings:
    # App settings
    app_name: str = "Melbourne Celebrant Portal"
    app_version: str = "2.0.0"
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./celebrant_portal.db")
    
    # CORS
    cors_origins: List[str] = ["*"]
    
    def __init__(self):
        # Handle database URL format conversion for Render
        if self.database_url.startswith("postgres://"):
            # Convert postgres:// to postgresql:// for SQLAlchemy compatibility
            self.database_url = self.database_url.replace("postgres://", "postgresql://", 1)
        
        # Set debug based on environment
        if self.environment.lower() == "production":
            self.debug = False
        
        # Validate required settings in production
        if self.environment.lower() == "production":
            if self.secret_key == "your-secret-key-here":
                raise ValueError("SECRET_KEY must be set in production")


# Create settings instance
settings = Settings()
