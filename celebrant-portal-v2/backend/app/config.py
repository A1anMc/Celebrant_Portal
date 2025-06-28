import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # App settings
    app_name: str = "Melbourne Celebrant Portal"
    app_version: str = "2.0.0"
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./celebrant_portal.db")
    
    # CORS
    cors_origins_str: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001,http://localhost:3002,http://localhost:3003,http://localhost:3004")
    
    @property
    def cors_origins(self) -> List[str]:
        """Get CORS origins with special handling for unified deployment."""
        if self.cors_origins_str == '["*"]' or self.cors_origins_str == "*":
            # In unified deployment on Render, allow all origins
            return ["*"]
        return [origin.strip() for origin in self.cors_origins_str.split(",")]
    
    # Email settings (optional)
    smtp_server: str = os.getenv("SMTP_SERVER", "")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from_email: str = os.getenv("SMTP_FROM_EMAIL", "noreply@melbournecelebrant.com")
    smtp_from_name: str = os.getenv("SMTP_FROM_NAME", "Melbourne Celebrant Portal")
    
    # File upload settings
    upload_folder: str = os.getenv("UPLOAD_FOLDER", "uploads")
    max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "app.log")
    
    # Security
    bcrypt_rounds: int = int(os.getenv("BCRYPT_ROUNDS", "12"))
    session_timeout: int = int(os.getenv("SESSION_TIMEOUT", "3600"))  # 1 hour
    
    # Database connection pool settings
    db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "5"))
    db_max_overflow: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    db_pool_timeout: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    
    # Redis (optional)
    redis_url: str = os.getenv("REDIS_URL", "")
    
    # JWT
    algorithm: str = "HS256"
    
    model_config = {"case_sensitive": False}

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
                raise ValueError("SECRET_KEY must be changed in production")

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        return self.environment.lower() == "development"


# Create settings instance
settings = Settings()

# Validate critical settings
if settings.is_production:
    if settings.secret_key == "your-secret-key-here":
        raise ValueError("SECRET_KEY must be changed in production")
    
    if settings.debug:
        raise ValueError("DEBUG must be False in production")
    
    # Note: CORS validation removed for unified deployment
    # In unified deployment, frontend and backend are on same host
