"""
Comprehensive health checks for all system components.
Provides detailed monitoring of database, cache, email, and external services.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import psutil
import redis
import smtplib
from sqlalchemy import text
from sqlalchemy.orm import Session

from ..database import get_db
from ..cache import redis_client
from ..email_service import email_service
from ..monitoring import logger

class HealthChecker:
    """Comprehensive health checking for all system components."""
    
    def __init__(self):
        self.health_status = {}
        self.last_check = None
        self.check_interval = 300  # 5 minutes
    
    async def run_full_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check of all systems."""
        start_time = time.time()
        
        health_results = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "checks": {},
            "performance": {},
            "errors": []
        }
        
        try:
            # Run all health checks
            checks = await asyncio.gather(
                self.check_database(),
                self.check_redis_cache(),
                self.check_email_service(),
                self.check_system_resources(),
                self.check_application_metrics(),
                return_exceptions=True
            )
            
            # Process results
            for i, check_result in enumerate(checks):
                if isinstance(check_result, Exception):
                    health_results["errors"].append(str(check_result))
                    health_results["overall_status"] = "degraded"
                else:
                    check_name = list(check_result.keys())[0]
                    health_results["checks"][check_name] = check_result[check_name]
                    
                    if check_result[check_name].get("status") == "unhealthy":
                        health_results["overall_status"] = "unhealthy"
            
            # Add performance metrics
            health_results["performance"]["check_duration"] = time.time() - start_time
            health_results["performance"]["memory_usage"] = self.get_memory_usage()
            health_results["performance"]["cpu_usage"] = self.get_cpu_usage()
            
            # Update last check time
            self.last_check = datetime.now()
            self.health_status = health_results
            
            logger.info("Health check completed", 
                       status=health_results["overall_status"],
                       duration=health_results["performance"]["check_duration"])
            
            return health_results
            
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "unhealthy",
                "error": str(e),
                "checks": {},
                "performance": {}
            }
    
    async def check_database(self) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        try:
            db = next(get_db())
            
            # Test basic connectivity
            start_time = time.time()
            result = db.execute(text("SELECT 1"))
            result.fetchone()
            query_time = time.time() - start_time
            
            # Test more complex query
            start_time = time.time()
            user_count = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
            complex_query_time = time.time() - start_time
            
            # Check database size
            db_size = db.execute(text("""
                SELECT pg_size_pretty(pg_database_size(current_database()))
            """)).scalar()
            
            return {
                "database": {
                    "status": "healthy",
                    "connection": "connected",
                    "query_time": round(query_time * 1000, 2),  # ms
                    "complex_query_time": round(complex_query_time * 1000, 2),  # ms
                    "user_count": user_count,
                    "database_size": db_size,
                    "last_check": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            return {
                "database": {
                    "status": "unhealthy",
                    "connection": "disconnected",
                    "error": str(e),
                    "last_check": datetime.now().isoformat()
                }
            }
    
    async def check_redis_cache(self) -> Dict[str, Any]:
        """Check Redis cache connectivity and performance."""
        try:
            # Test basic connectivity
            start_time = time.time()
            redis_client.ping()
            ping_time = time.time() - start_time
            
            # Test set/get operations
            start_time = time.time()
            redis_client.set("health_check", "test", ex=60)
            redis_client.get("health_check")
            operation_time = time.time() - start_time
            
            # Get Redis info
            info = redis_client.info()
            
            return {
                "redis": {
                    "status": "healthy",
                    "connection": "connected",
                    "ping_time": round(ping_time * 1000, 2),  # ms
                    "operation_time": round(operation_time * 1000, 2),  # ms
                    "used_memory": info.get("used_memory_human"),
                    "connected_clients": info.get("connected_clients"),
                    "total_commands_processed": info.get("total_commands_processed"),
                    "last_check": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error("Redis health check failed", error=str(e))
            return {
                "redis": {
                    "status": "unhealthy",
                    "connection": "disconnected",
                    "error": str(e),
                    "last_check": datetime.now().isoformat()
                }
            }
    
    async def check_email_service(self) -> Dict[str, Any]:
        """Check email service connectivity."""
        try:
            # Test SMTP connection
            start_time = time.time()
            
            with smtplib.SMTP(email_service.smtp_server, email_service.smtp_port) as server:
                server.starttls()
                server.login(email_service.smtp_username, email_service.smtp_password)
            
            connection_time = time.time() - start_time
            
            return {
                "email": {
                    "status": "healthy",
                    "connection": "connected",
                    "connection_time": round(connection_time * 1000, 2),  # ms
                    "smtp_server": email_service.smtp_server,
                    "last_check": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error("Email service health check failed", error=str(e))
            return {
                "email": {
                    "status": "unhealthy",
                    "connection": "disconnected",
                    "error": str(e),
                    "last_check": datetime.now().isoformat()
                }
            }
    
    async def check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            
            # Disk usage
            disk = psutil.disk_usage('/')
            
            # Network I/O
            network = psutil.net_io_counters()
            
            return {
                "system": {
                    "status": "healthy" if cpu_percent < 80 and memory.percent < 80 else "warning",
                    "cpu_usage": round(cpu_percent, 2),
                    "memory_usage": round(memory.percent, 2),
                    "memory_available": f"{memory.available // (1024**3)} GB",
                    "disk_usage": round(disk.percent, 2),
                    "disk_free": f"{disk.free // (1024**3)} GB",
                    "network_bytes_sent": network.bytes_sent,
                    "network_bytes_recv": network.bytes_recv,
                    "last_check": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error("System resources health check failed", error=str(e))
            return {
                "system": {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_check": datetime.now().isoformat()
                }
            }
    
    async def check_application_metrics(self) -> Dict[str, Any]:
        """Check application-specific metrics."""
        try:
            from ..monitoring import metrics
            
            current_metrics = metrics.get_metrics()
            
            # Calculate error rate
            total_requests = current_metrics.get("request_count", 0)
            error_count = current_metrics.get("error_count", 0)
            error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0
            
            # Check response times
            avg_response_time = current_metrics.get("avg_response_time", 0)
            
            return {
                "application": {
                    "status": "healthy" if error_rate < 5 and avg_response_time < 1000 else "warning",
                    "total_requests": total_requests,
                    "error_count": error_count,
                    "error_rate": round(error_rate, 2),
                    "avg_response_time": round(avg_response_time, 2),
                    "database_queries": current_metrics.get("database_queries", 0),
                    "database_errors": current_metrics.get("database_errors", 0),
                    "auth_failures": current_metrics.get("auth_failures", 0),
                    "last_check": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error("Application metrics health check failed", error=str(e))
            return {
                "application": {
                    "status": "unhealthy",
                    "error": str(e),
                    "last_check": datetime.now().isoformat()
                }
            }
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage."""
        try:
            memory = psutil.virtual_memory()
            return {
                "total": f"{memory.total // (1024**3)} GB",
                "available": f"{memory.available // (1024**3)} GB",
                "percent": round(memory.percent, 2)
            }
        except Exception:
            return {"error": "Unable to get memory usage"}
    
    def get_cpu_usage(self) -> Dict[str, Any]:
        """Get current CPU usage."""
        try:
            return {
                "percent": round(psutil.cpu_percent(interval=1), 2),
                "count": psutil.cpu_count()
            }
        except Exception:
            return {"error": "Unable to get CPU usage"}
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of the last health check."""
        if not self.health_status:
            return {"status": "no_health_check_performed"}
        
        return {
            "overall_status": self.health_status.get("overall_status"),
            "last_check": self.health_status.get("timestamp"),
            "check_duration": self.health_status.get("performance", {}).get("check_duration"),
            "component_status": {
                name: check.get("status", "unknown")
                for name, check in self.health_status.get("checks", {}).items()
            }
        }
    
    def should_alert(self, health_results: Dict[str, Any]) -> bool:
        """Determine if an alert should be sent based on health results."""
        # Alert if overall status is unhealthy
        if health_results.get("overall_status") == "unhealthy":
            return True
        
        # Alert if any critical component is unhealthy
        critical_components = ["database", "redis"]
        for component in critical_components:
            if component in health_results.get("checks", {}):
                if health_results["checks"][component].get("status") == "unhealthy":
                    return True
        
        # Alert if error rate is too high
        app_metrics = health_results.get("checks", {}).get("application", {})
        if app_metrics.get("error_rate", 0) > 10:  # 10% error rate
            return True
        
        return False

# Global health checker instance
health_checker = HealthChecker()
