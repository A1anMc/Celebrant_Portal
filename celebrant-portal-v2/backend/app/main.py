from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import logging
import sys
import traceback

from app.config import settings
from app.auth.router import router as auth_router
from app.api import dashboard, couples, legal_forms
from app.database import create_tables, engine
from app.models.user import User
from app.auth.utils import get_password_hash
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Create session for database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Melbourne Celebrant Portal...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Database URL prefix: {settings.database_url[:20]}...")
    
    try:
        # Test database connection
        logger.info("Testing database connection...")
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        
        # Create tables
        logger.info("Creating database tables...")
        create_tables()
        logger.info("Database tables created successfully")
        
        # Create default admin user if it doesn't exist
        logger.info("Checking for admin user...")
        db = SessionLocal()
        try:
            admin_user = db.query(User).filter(User.email == "admin@melbournecelebrant.com").first()
            if not admin_user:
                logger.info("Creating default admin user...")
                admin_user = User(
                    email="admin@melbournecelebrant.com",
                    first_name="Admin",
                    last_name="User",
                    phone="0400000000",
                    is_active=True,
                    is_admin=True,
                    hashed_password=get_password_hash("admin123")
                )
                db.add(admin_user)
                db.commit()
                logger.info("Default admin user created successfully")
            else:
                logger.info("Admin user already exists")
        except Exception as e:
            logger.error(f"Error creating admin user: {e}")
            db.rollback()
        finally:
            db.close()
            
        logger.info("Application startup completed successfully")
        yield
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Don't raise the exception - let the app start even if DB is not available
        # This allows us to see the error in Render logs
        yield
    
    logger.info("Application shutdown")


# Create FastAPI app with lifespan
app = FastAPI(
    title="Melbourne Celebrant Portal",
    description="A comprehensive portal for wedding celebrants in Melbourne",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(couples.router, prefix="/api/couples", tags=["Couples"])
app.include_router(legal_forms.router, prefix="/api/legal-forms", tags=["Legal Forms"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Melbourne Celebrant Portal API",
        "version": "2.0.0",
        "status": "running",
        "environment": settings.environment
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test database connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy",
        "database": db_status,
        "environment": settings.environment,
        "version": "2.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 