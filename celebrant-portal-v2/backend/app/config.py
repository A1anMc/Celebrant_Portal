from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Application settings
    app_name: str = "Melbourne Celebrant Portal API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database settings
    database_url: str = "sqlite:///./celebrant_portal.db"
    
    # Security settings
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # CORS settings
    cors_origins: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Logging settings
    log_level: str = "INFO"
    
    # File upload settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    upload_directory: str = "uploads"
    
    # Email settings (for future use)
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create global settings instance
settings = Settings() 