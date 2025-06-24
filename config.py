import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production-2024'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database', 'celebrant.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # WTF/CSRF Configuration
    WTF_CSRF_ENABLED = False  # Temporarily disabled for testing
    WTF_CSRF_TIME_LIMIT = None  # No time limit for CSRF tokens
    
    # Email configuration
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Celery configuration
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # Email settings for notifications
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@celebrant-portal.com'
    
    # Base URL for portal links in emails
    BASE_URL = os.environ.get('BASE_URL') or 'http://localhost:5000'
    
    # Gmail API configuration
    GMAIL_TOKEN_FILE = 'token.json'
    GMAIL_CREDENTIALS_FILE = 'credentials.json'

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    # Use SQLite for development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database', 'celebrant_dev.db')

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    # Use in-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL', 'sqlite:///:memory:')

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # Ensure HTTPS in production
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    
    # Get the database URL from environment variable
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if database_url.startswith('postgres://'):
            # Heroku provides DATABASE_URL starting with 'postgres://', but SQLAlchemy requires 'postgresql://'
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        elif database_url.startswith('mysql://'):
            # MySQL URL - add PyMySQL driver
            if '?' in database_url:
                database_url = database_url.replace('mysql://', 'mysql+pymysql://', 1)
            else:
                database_url = database_url.replace('mysql://', 'mysql+pymysql://', 1) + '?charset=utf8mb4'
    
    SQLALCHEMY_DATABASE_URI = database_url or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database', 'celebrant_prod.db')

# Dictionary to map environment names to config objects
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 