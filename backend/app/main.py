from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.config import settings
from app.database import create_tables
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Professional celebrant practice management system",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware (optional, for production)
if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.vercel.app"]
    )


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    try:
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "message": "Melbourne Celebrant Portal API",
        "version": settings.app_version,
        "status": "healthy"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": "2024-12-30T12:00:00Z"}


# Import and include routers
from app.auth.router import router as auth_router
from app.api.couples import router as couples_router
from app.api.ceremonies import router as ceremonies_router
from app.api.invoices import router as invoices_router
from app.api.legal_forms import router as legal_forms_router
from app.api.templates import router as templates_router
from app.api.travel import router as travel_router
from app.api.dashboard import router as dashboard_router
from app.api.reports import router as reports_router

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(couples_router, prefix="/api/couples", tags=["Couples"])
app.include_router(ceremonies_router, prefix="/api/ceremonies", tags=["Ceremonies"])
app.include_router(invoices_router, prefix="/api/invoices", tags=["Invoices"])
app.include_router(legal_forms_router, prefix="/api/legal-forms", tags=["Legal Forms"])
app.include_router(templates_router, prefix="/api/templates", tags=["Templates"])
app.include_router(travel_router, prefix="/api/travel", tags=["Travel"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(reports_router, prefix="/api/reports", tags=["Reports"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    ) 