from pydantic_settings import BaseSettings
from typing import List
import os
import secrets


class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/celebrant_portal")
    database_url_test: str = os.getenv("DATABASE_URL_TEST", "postgresql://username:password@localhost:5432/celebrant_portal_test")
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Application
    app_name: str = "Melbourne Celebrant Portal API"
    app_version: str = "2.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # CORS Origins - Production ready
    allowed_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://melbourne-celebrant-portal.vercel.app",
        "https://*.vercel.app",
        "https://amelbournecelebrant.com.au",
        "https://www.amelbournecelebrant.com.au"
    ]
    
    # Email (Brevo/SendinBlue for free tier)
    smtp_host: str = os.getenv("SMTP_HOST", "smtp-relay.brevo.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    from_email: str = os.getenv("FROM_EMAIL", "noreply@amelbournecelebrant.com.au")
    
    # File Upload
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    upload_dir: str = os.getenv("UPLOAD_DIR", "uploads")
    
    # Production settings
    @property
    def is_production(self) -> bool:
        return self.environment == "production"
    
    @property
    def database_url_sync(self) -> str:
        """Convert async database URL to sync for SQLAlchemy."""
        return self.database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()

# Ensure upload directory exists
if not settings.is_production:
    os.makedirs(settings.upload_dir, exist_ok=True) 