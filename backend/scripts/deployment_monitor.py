#!/usr/bin/env python3
"""
Deployment Monitor - Robust AI Agent Protocol Implementation
Implements continuous validation and feedback loops for bulletproof deployment.
"""

import os
import sys
import time
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import subprocess
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeploymentMonitor:
    """Implements the Robust AI Agent Protocol for deployment monitoring."""
    
    def __init__(self, backend_url: str, frontend_url: str):
        self.backend_url = backend_url
        self.frontend_url = frontend_url
        self.health_checks = []
        self.failures = []
        self.successes = []
        
    def log_event(self, event_type: str, message: str, details: Dict = None):
        """Log events with structured data for monitoring."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "message": message,
            "details": details or {}
        }
        
        if event_type == "SUCCESS":
            self.successes.append(event)
            logger.info(f"✅ {message}")
        elif event_type == "FAILURE":
            self.failures.append(event)
            logger.error(f"❌ {message}")
        elif event_type == "WARNING":
            logger.warning(f"⚠️ {message}")
        else:
            logger.info(f"ℹ️ {message}")
            
        self.health_checks.append(event)
        
    def check_backend_health(self) -> bool:
        """Phase 1: Initial State & Pre-Execution Checks - Backend Health."""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_event("SUCCESS", "Backend health check passed", {
                    "status": data.get("status"),
                    "version": data.get("version"),
                    "response_time": response.elapsed.total_seconds()
                })
                return True
            else:
                self.log_event("FAILURE", f"Backend health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_event("FAILURE", f"Backend health check error: {str(e)}")
            return False
    
    def check_frontend_health(self) -> bool:
        """Phase 1: Initial State & Pre-Execution Checks - Frontend Health."""
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                self.log_event("SUCCESS", "Frontend health check passed", {
                    "response_time": response.elapsed.total_seconds()
                })
                return True
            else:
                self.log_event("FAILURE", f"Frontend health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_event("FAILURE", f"Frontend health check error: {str(e)}")
            return False
    
    def check_environment_variables(self) -> bool:
        """Phase 1: Dependency Audit & Security Scan - Environment Variables."""
        critical_vars = [
            "DATABASE_URL",
            "SECRET_KEY", 
            "ALLOWED_ORIGINS"
        ]
        
        missing_vars = []
        for var in critical_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.log_event("FAILURE", f"Missing critical environment variables: {missing_vars}")
            return False
        else:
            self.log_event("SUCCESS", "All critical environment variables configured")
            return True
    
    def check_api_endpoints(self) -> bool:
        """Phase 2: Execution & Real-Time Monitoring - API Endpoints."""
        endpoints = [
            "/api/v1/auth/login",
            "/api/v1/couples/",
            "/api/v1/ceremonies/",
            "/api/v1/invoices/"
        ]
        
        failed_endpoints = []
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                if response.status_code not in [200, 401, 405]:  # 401/405 are expected for unauthenticated requests
                    failed_endpoints.append(f"{endpoint} ({response.status_code})")
            except Exception as e:
                failed_endpoints.append(f"{endpoint} (error: {str(e)})")
        
        if failed_endpoints:
            self.log_event("FAILURE", f"API endpoint check failed: {failed_endpoints}")
            return False
        else:
            self.log_event("SUCCESS", "All API endpoints responding")
            return True
    
    def check_cors_configuration(self) -> bool:
        """Phase 2: Security Hardening - CORS Configuration."""
        try:
            # Test CORS headers
            response = requests.options(f"{self.backend_url}/api/v1/auth/login", 
                                      headers={"Origin": "https://test.vercel.app"})
            
            cors_headers = response.headers.get("Access-Control-Allow-Origin")
            if cors_headers:
                self.log_event("SUCCESS", "CORS configuration working", {
                    "allow_origin": cors_headers
                })
                return True
            else:
                self.log_event("FAILURE", "CORS headers not found")
                return False
        except Exception as e:
            self.log_event("FAILURE", f"CORS check error: {str(e)}")
            return False
    
    def run_comprehensive_check(self) -> Dict:
        """Phase 3: Continuous Validation & Feedback Loop - Comprehensive Check."""
        self.log_event("INFO", "Starting comprehensive deployment validation")
        
        checks = {
            "backend_health": self.check_backend_health(),
            "frontend_health": self.check_frontend_health(),
            "environment_variables": self.check_environment_variables(),
            "api_endpoints": self.check_api_endpoints(),
            "cors_configuration": self.check_cors_configuration()
        }
        
        # Calculate overall health
        passed_checks = sum(checks.values())
        total_checks = len(checks)
        health_percentage = (passed_checks / total_checks) * 100
        
        # Generate comprehensive report
        report = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": health_percentage,
            "passed_checks": passed_checks,
            "total_checks": total_checks,
            "check_results": checks,
            "recent_events": self.health_checks[-10:],  # Last 10 events
            "failure_count": len(self.failures),
            "success_count": len(self.successes)
        }
        
        # Log overall status
        if health_percentage == 100:
            self.log_event("SUCCESS", f"🎉 All checks passed! Health: {health_percentage}%")
        elif health_percentage >= 80:
            self.log_event("WARNING", f"⚠️ Most checks passed. Health: {health_percentage}%")
        else:
            self.log_event("FAILURE", f"❌ Critical issues detected. Health: {health_percentage}%")
        
        return report
    
    def generate_alert_message(self, report: Dict) -> str:
        """Generate alert message for communication tools."""
        health = report["overall_health"]
        
        if health == 100:
            return f"✅ **Deployment Health Check PASSED**\n" \
                   f"• Health Score: {health}%\n" \
                   f"• All {report['total_checks']} checks successful\n" \
                   f"• System is fully operational"
        elif health >= 80:
            return f"⚠️ **Deployment Health Check WARNING**\n" \
                   f"• Health Score: {health}%\n" \
                   f"• {report['passed_checks']}/{report['total_checks']} checks passed\n" \
                   f"• Monitor for potential issues"
        else:
            return f"❌ **Deployment Health Check FAILED**\n" \
                   f"• Health Score: {health}%\n" \
                   f"• {report['passed_checks']}/{report['total_checks']} checks passed\n" \
                   f"• Immediate attention required"
    
    def continuous_monitoring(self, interval_seconds: int = 300):
        """Continuous monitoring with feedback loop."""
        self.log_event("INFO", f"Starting continuous monitoring (interval: {interval_seconds}s)")
        
        while True:
            try:
                report = self.run_comprehensive_check()
                alert = self.generate_alert_message(report)
                
                # Log the alert (in production, this would go to Slack/Teams)
                print(f"\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(alert)
                
                # Wait for next check
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                self.log_event("INFO", "Continuous monitoring stopped by user")
                break
            except Exception as e:
                self.log_event("FAILURE", f"Monitoring error: {str(e)}")
                time.sleep(interval_seconds)

def main():
    """Main execution function."""
    # Configuration
    backend_url = os.getenv("BACKEND_URL", "https://melbourne-celebrant-portal-backend.onrender.com")
    frontend_url = os.getenv("FRONTEND_URL", "https://celebrant-portal-ah8ssgciz-alans-projects-baf4c067.vercel.app")
    
    monitor = DeploymentMonitor(backend_url, frontend_url)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        # Continuous monitoring mode
        monitor.continuous_monitoring()
    else:
        # Single check mode
        report = monitor.run_comprehensive_check()
        print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
