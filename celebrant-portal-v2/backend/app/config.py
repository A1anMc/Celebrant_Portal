from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # App settings
    app_name: str = "Melbourne Celebrant Portal"
    app_version: str = "2.0.0"
    environment: str = "development"
    debug: bool = True
    
    # Security
    secret_key: str = "your-secret-key-here"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30
    
    # Database
    database_url: str = "sqlite:///./celebrant_portal.db"
    
    # CORS
    cors_origins: List[str] = ["*"]
    
    # Logging
    log_level: str = "INFO"
    
    # Google Maps API
    google_maps_api_key: Optional[str] = None
    
    # Celebrant business settings
    celebrant_home_address: str = "Melbourne, VIC, Australia"
    travel_fee_per_km: float = 1.50
    minimum_travel_fee: float = 50.00
    maximum_travel_distance: int = 100
    
    # Email settings (Brevo)
    brevo_api_key: Optional[str] = None
    brevo_sender_email: str = "admin@melbournecelebrant.com"
    brevo_sender_name: str = "Melbourne Celebrant"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
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