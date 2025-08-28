from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Create engine based on database URL
def create_database_engine():
    """Create database engine with fallback to SQLite if PostgreSQL fails."""
    if settings.database_url.startswith("sqlite"):
        return create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False}
        )
    else:
        # PostgreSQL for production - use psycopg3 dialect
        try:
            return create_engine(
                settings.database_url.replace("postgresql://", "postgresql+psycopg://"),
                pool_pre_ping=True,
                pool_recycle=300
            )
        except Exception as e:
            print(f"Warning: PostgreSQL connection failed: {e}")
            print("Falling back to SQLite database")
            # Fallback to SQLite
            return create_engine(
                "sqlite:///./celebrant_portal.db",
                connect_args={"check_same_thread": False}
            )

engine = create_database_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create metadata and base
metadata = MetaData()
Base = declarative_base(metadata=metadata)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create all tables
def create_tables():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Database connection error: {e}")
        raise