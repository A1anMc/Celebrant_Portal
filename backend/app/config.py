from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://username:password@localhost:5432/celebrant_portal"
    database_url_test: str = "postgresql://username:password@localhost:5432/celebrant_portal_test"
    
    # Security
    secret_key: str = "your-super-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Application
    app_name: str = "Melbourne Celebrant Portal API"
    app_version: str = "2.0.0"
    debug: bool = True
    allowed_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Email (Optional)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    
    # File Upload
    max_file_size: int = 10485760  # 10MB
    upload_dir: str = "uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True) 