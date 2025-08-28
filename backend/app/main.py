from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
import time
from typing import Callable
import secrets
from datetime import datetime

from .core.config import settings, get_allowed_origins
from .core.database import create_tables, engine, Base
from .api.v1 import auth, couples, ceremonies, invoices
from .core.monitoring import RequestLogger, HealthChecker, setup_logging

# Setup logging
setup_logging(settings.log_level if hasattr(settings, 'log_level') else "INFO")

# Create tables on startup
create_tables()

# Initialize FastAPI app
app = FastAPI(
    title="Melbourne Celebrant Portal API",
    description="A professional portal for wedding celebrants to manage couples, ceremonies, and invoices",
    version="0.2.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Add request logging middleware
app.middleware("http")(RequestLogger.log_request)

# Include API v1 routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(couples.router, prefix="/api/v1")
app.include_router(ceremonies.router, prefix="/api/v1")
app.include_router(invoices.router, prefix="/api/v1")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Disable TrustedHostMiddleware for development
# app.add_middleware(
#     TrustedHostMiddleware, 
#     allowed_hosts=settings.allowed_origins
# )

app.add_middleware(
    SessionMiddleware, 
    secret_key=settings.secret_key
)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app,
        calls_limit: int = 100,
        time_window: int = 60
    ):
        super().__init__(app)
        self.calls_limit = calls_limit
        self.time_window = time_window
        self.requests = {}

    async def dispatch(self, request: Request, call_next: Callable):
        # Skip rate limiting for health check endpoint
        if request.url.path == "/health":
            return await call_next(request)
            
        # Safely get client IP with fallback
        client_ip = "unknown"
        if request.client:
            client_ip = request.client.host
        elif "x-forwarded-for" in request.headers:
            client_ip = request.headers["x-forwarded-for"].split(",")[0].strip()
        elif "x-real-ip" in request.headers:
            client_ip = request.headers["x-real-ip"]
        
        current_time = time.time()

        # Clean up old requests
        self.requests = {
            ip: reqs for ip, reqs in self.requests.items()
            if current_time - reqs["timestamp"] < self.time_window
        }

        # Check rate limit
        if client_ip in self.requests:
            if self.requests[client_ip]["count"] >= self.calls_limit:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests"}
                )
            self.requests[client_ip]["count"] += 1
        else:
            self.requests[client_ip] = {
                "count": 1,
                "timestamp": current_time
            }

        response = await call_next(request)
        return response

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Temporarily disable CSRF for development
# @CsrfProtect.load_config
# def get_csrf_config():
#     return {
#         "secret_key": settings.csrf_token_secret
#     }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "0.2.0",
        "message": "Melbourne Celebrant Portal is running"
    }

@app.get("/metrics")
async def get_metrics():
    """Get application metrics."""
    from .core.monitoring import metrics
    return metrics.get_metrics()

# Root endpoint
@app.get("/")
def read_root():
    """Root endpoint."""
    return {
        "message": "Melbourne Celebrant Portal API",
        "version": "0.2.0",
        "docs_url": "/docs" if settings.debug else "Documentation disabled in production"
    }

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    # Add security headers to all responses
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'; img-src 'self' data:; script-src 'self'"
    return response

@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return JSONResponse(
        status_code=403,
        content={"detail": "CSRF token missing or invalid"}
    )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    if settings.debug:
        raise exc
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    ) 