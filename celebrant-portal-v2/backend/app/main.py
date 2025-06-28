from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse, Response
from contextlib import asynccontextmanager
import logging
import sys
import traceback
import os
import httpx
from pathlib import Path

from app.config import settings
from app.auth.router import router as auth_router
from app.api import dashboard, couples, legal_forms
from app.database import create_tables, engine, get_db, Base
from app.models.user import User
from app.auth.utils import get_password_hash
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler()
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
        with next(get_db()) as db:
            try:
                admin_user = db.query(User).filter(User.email == "admin@melbournecelebrant.com").first()
                if not admin_user:
                    logger.info("Creating default admin user...")
                    admin_user = User(
                        email="admin@melbournecelebrant.com",
                        name="Admin User",
                        phone="0400000000",
                        is_active=True,
                        is_verified=True,
                        role="admin",
                        password_hash=get_password_hash("admin123")
                    )
                    db.add(admin_user)
                    db.commit()
                    logger.info("Default admin user created successfully")
                else:
                    logger.info("Admin user already exists")
            except Exception as e:
                logger.error(f"Error creating admin user: {e}")
                db.rollback()
            
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
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin"],
    expose_headers=["Content-Length", "Authorization"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(couples.router, prefix="/api/couples", tags=["Couples"])
app.include_router(legal_forms.router, prefix="/api/legal-forms", tags=["Legal Forms"])

# Mount static files for Next.js frontend
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    # Serve Next.js static files
    app.mount("/static", StaticFiles(directory=str(frontend_dir / "public")), name="static")
    app.mount("/_next", StaticFiles(directory=str(frontend_dir / ".next" / "static")), name="nextjs")

# Proxy requests to Next.js frontend
@app.middleware("http")
async def proxy_frontend(request: Request, call_next):
    """Proxy non-API requests to Next.js frontend."""
    
    # Let API requests pass through
    if request.url.path.startswith("/api") or request.url.path.startswith("/docs") or request.url.path.startswith("/openapi.json") or request.url.path == "/health":
        response = await call_next(request)
        return response
    
    # Proxy all other requests to Next.js frontend
    try:
        async with httpx.AsyncClient() as client:
            frontend_url = f"http://localhost:3000{request.url.path}"
            if request.url.query:
                frontend_url += f"?{request.url.query}"
            
            # Forward the request to Next.js
            response = await client.request(
                method=request.method,
                url=frontend_url,
                headers=dict(request.headers),
                content=await request.body() if request.method in ["POST", "PUT", "PATCH"] else None,
                timeout=30.0
            )
            
            # Return the response from Next.js
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type")
            )
    except Exception as e:
        logger.error(f"Error proxying to frontend: {e}")
        # Fallback to API response for root
        if request.url.path == "/":
            return {
                "message": "Melbourne Celebrant Portal API",
                "version": "2.0.0",
                "status": "running",
                "environment": settings.environment,
                "frontend_error": str(e)
            }
        # For other paths, return 404
        raise HTTPException(status_code=404, detail="Page not found")


@app.get("/api")
async def api_root():
    """API root endpoint."""
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
    port = int(os.getenv("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=settings.debug,
        log_level="info"
    ) 