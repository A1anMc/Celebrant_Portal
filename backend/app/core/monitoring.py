"""
Monitoring and logging configuration for the Melbourne Celebrant Portal.
Provides structured logging, metrics collection, and health checks.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import contextmanager
from functools import wraps
import json
import traceback

from fastapi import Request, Response
from fastapi.responses import JSONResponse
import structlog
from structlog.stdlib import LoggerFactory
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import StreamingResponse

# Configure structlog for structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Create logger instance
logger = structlog.get_logger()

# Metrics storage (in production, use Prometheus, DataDog, etc.)
class MetricsCollector:
    """Simple metrics collector for application monitoring."""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {
            "request_count": 0,
            "error_count": 0,
            "response_times": [],
            "endpoint_usage": {},
            "database_queries": 0,
            "database_errors": 0,
            "auth_failures": 0,
            "successful_logins": 0,
            "failed_logins": 0,
        }
    
    def increment(self, metric: str, value: int = 1):
        """Increment a metric counter."""
        if metric in self.metrics:
            if isinstance(self.metrics[metric], int):
                self.metrics[metric] += value
            elif isinstance(self.metrics[metric], list):
                self.metrics[metric].append(value)
    
    def record_endpoint_usage(self, endpoint: str, method: str):
        """Record endpoint usage."""
        key = f"{method} {endpoint}"
        if key not in self.metrics["endpoint_usage"]:
            self.metrics["endpoint_usage"][key] = 0
        self.metrics["endpoint_usage"][key] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        # Calculate average response time
        response_times = self.metrics["response_times"]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            **self.metrics,
            "avg_response_time": avg_response_time,
            "timestamp": datetime.now().isoformat()
        }
    
    def reset(self):
        """Reset metrics (useful for testing)."""
        self.metrics = {
            "request_count": 0,
            "error_count": 0,
            "response_times": [],
            "endpoint_usage": {},
            "database_queries": 0,
            "database_errors": 0,
            "auth_failures": 0,
            "successful_logins": 0,
            "failed_logins": 0,
        }

# Global metrics collector
metrics = MetricsCollector()

class APIMonitor:
    """API monitoring and analytics."""
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
        self.endpoint_stats = {}
    
    def log_request(self, request: Request, response: Response, duration: float):
        """Log API request details."""
        self.request_count += 1
        
        # Track endpoint statistics
        endpoint = request.url.path
        if endpoint not in self.endpoint_stats:
            self.endpoint_stats[endpoint] = {
                "count": 0,
                "errors": 0,
                "avg_response_time": 0,
                "total_response_time": 0
            }
        
        self.endpoint_stats[endpoint]["count"] += 1
        self.endpoint_stats[endpoint]["total_response_time"] += duration
        
        # Track response times
        self.response_times.append(duration)
        if len(self.response_times) > 1000:  # Keep last 1000 requests
            self.response_times.pop(0)
        
        # Log request details
        log_data = {
            "event": "api_request",
            "method": request.method,
            "path": endpoint,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "user_agent": request.headers.get("user-agent", ""),
            "ip": request.client.host if request.client else "unknown",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if response.status_code >= 400:
            self.error_count += 1
            self.endpoint_stats[endpoint]["errors"] += 1
            log_data["level"] = "error"
        else:
            log_data["level"] = "info"
        
        logger.info("API Request", **log_data)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current API statistics."""
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        
        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate": (self.error_count / self.request_count * 100) if self.request_count > 0 else 0,
            "avg_response_time_ms": round(avg_response_time * 1000, 2),
            "endpoint_stats": self.endpoint_stats,
            "timestamp": datetime.utcnow().isoformat()
        }

# Global API monitor instance
api_monitor = APIMonitor()

class RequestLogger(BaseHTTPMiddleware):
    """Middleware to log all requests and track API performance."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Skip logging for health checks
        if request.url.path == "/health":
            return await call_next(request)
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            api_monitor.log_request(request, response, duration)
            return response
        except Exception as e:
            duration = time.time() - start_time
            # Create a mock response for logging
            response = Response(
                content=json.dumps({"detail": "Internal server error"}),
                status_code=500,
                media_type="application/json"
            )
            api_monitor.log_request(request, response, duration)
            raise

class DatabaseMonitor:
    """Monitor database operations and performance."""
    
    @staticmethod
    @contextmanager
    def monitor_query(operation: str, table: Optional[str] = None):
        """Monitor database query execution."""
        start_time = time.time()
        metrics.increment("database_queries")
        
        try:
            yield
            process_time = time.time() - start_time
            
            logger.debug(
                "Database query completed",
                operation=operation,
                table=table,
                process_time=process_time,
            )
            
        except Exception as e:
            metrics.increment("database_errors")
            process_time = time.time() - start_time
            
            logger.error(
                "Database query failed",
                operation=operation,
                table=table,
                error=str(e),
                process_time=process_time,
            )
            raise

class AuthMonitor:
    """Monitor authentication events."""
    
    @staticmethod
    def log_successful_login(email: str, user_id: int):
        """Log successful login attempt."""
        metrics.increment("successful_logins")
        logger.info(
            "Successful login",
            email=email,
            user_id=user_id,
        )
    
    @staticmethod
    def log_failed_login(email: str, reason: str, ip_address: Optional[str] = None):
        """Log failed login attempt."""
        metrics.increment("failed_logins")
        logger.warning(
            "Failed login attempt",
            email=email,
            reason=reason,
            ip_address=ip_address,
        )
    
    @staticmethod
    def log_auth_failure(operation: str, reason: str, user_id: Optional[int] = None):
        """Log authentication failure."""
        metrics.increment("auth_failures")
        logger.warning(
            "Authentication failure",
            operation=operation,
            reason=reason,
            user_id=user_id,
        )

def monitor_function(func_name: str):
    """Decorator to monitor function execution."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                process_time = time.time() - start_time
                
                logger.debug(
                    "Function completed",
                    function=func_name,
                    process_time=process_time,
                )
                
                return result
                
            except Exception as e:
                process_time = time.time() - start_time
                metrics.increment("error_count")
                
                logger.error(
                    "Function failed",
                    function=func_name,
                    error=str(e),
                    process_time=process_time,
                )
                raise
        
        return wrapper
    return decorator

class HealthChecker:
    """Health check utilities for the application."""
    
    @staticmethod
    async def check_database_health() -> Dict[str, Any]:
        """Check database connectivity and health."""
        try:
            from .database import get_db
            from sqlalchemy import text
            
            db = next(get_db())
            result = db.execute(text("SELECT 1"))
            result.fetchone()
            
            return {
                "status": "healthy",
                "database": "connected",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return {
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    @staticmethod
    async def check_application_health() -> Dict[str, Any]:
        """Comprehensive application health check."""
        db_health = await HealthChecker.check_database_health()
        
        # Get current metrics
        current_metrics = metrics.get_metrics()
        
        # Determine overall health
        overall_status = "healthy"
        if db_health["status"] == "unhealthy":
            overall_status = "unhealthy"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "version": "0.2.0",
            "components": {
                "database": db_health,
            },
            "metrics": {
                "request_count": current_metrics["request_count"],
                "error_count": current_metrics["error_count"],
                "avg_response_time": current_metrics["avg_response_time"],
            }
        }

# Initialize logging configuration
def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(message)s",
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    logger.info("Logging system initialized", log_level=log_level)

