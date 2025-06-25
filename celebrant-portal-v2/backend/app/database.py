from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Configure engine based on database type
if settings.database_url.startswith("postgresql://") or settings.database_url.startswith("postgres://"):
    # PostgreSQL configuration
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        echo=settings.debug,
        pool_size=10,
        max_overflow=20
    )
else:
    # SQLite configuration (for development)
    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
        echo=settings.debug,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
            "timeout": 20
        }
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db() -> Session:
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    try:
        # Import all models to ensure they are registered with Base
        from app.models import user, couple, ceremony, invoice, legal_form, template, travel_log
        
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def drop_tables():
    """Drop all database tables (use with caution)."""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise 