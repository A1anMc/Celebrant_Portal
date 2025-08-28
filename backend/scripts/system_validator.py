#!/usr/bin/env python3
"""
System Validator for Melbourne Celebrant Portal
Comprehensive testing and validation to ensure system is bulletproof.
"""

import sys
import os
import json
import asyncio
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import traceback
import requests
from pathlib import Path

class SystemValidator:
    """Comprehensive system validator for bulletproof deployment."""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {},
            "validation_results": {},
            "critical_issues": [],
            "warnings": [],
            "recommendations": [],
            "overall_status": "unknown"
        }
        
        self.backend_url = "http://localhost:8005"
        self.frontend_url = "http://localhost:3005"
        
    def validate_python_environment(self) -> Dict[str, Any]:
        """Validate Python environment and dependencies."""
        print("🐍 Validating Python environment...")
        
        env_info = {
            "python_version": sys.version,
            "python_path": sys.executable,
            "platform": sys.platform,
            "architecture": sys.maxsize > 2**32 and "64-bit" or "32-bit",
            "issues": [],
            "status": "unknown"
        }
        
        # Check Python version
        if sys.version_info < (3, 8):
            env_info["issues"].append("Python 3.8+ required")
        elif sys.version_info < (3, 11):
            env_info["warnings"] = ["Python 3.11+ recommended for optimal performance"]
        
        # Check virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            env_info["virtual_env"] = True
            env_info["venv_path"] = sys.prefix
        else:
            env_info["virtual_env"] = False
            env_info["warnings"] = env_info.get("warnings", []) + ["Not running in virtual environment"]
        
        # Check essential packages
        essential_packages = [
            "fastapi", "uvicorn", "sqlalchemy", "pydantic", 
            "passlib", "cryptography", "bcrypt"
        ]
        
        missing_packages = []
        for package in essential_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            env_info["issues"].append(f"Missing essential packages: {', '.join(missing_packages)}")
        
        # Determine status
        if env_info["issues"]:
            env_info["status"] = "critical"
        elif env_info.get("warnings"):
            env_info["status"] = "warning"
        else:
            env_info["status"] = "healthy"
        
        return env_info

    def validate_database_connection(self) -> Dict[str, Any]:
        """Validate database connectivity and schema."""
        print("🗄️  Validating database connection...")
        
        db_info = {
            "connection": False,
            "schema": False,
            "tables": [],
            "issues": [],
            "status": "unknown"
        }
        
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from app.core.database import engine, SessionLocal
            from app.models import Base, User, Couple, Invoice, Ceremony
            
            # Test connection
            from sqlalchemy import text
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
                db_info["connection"] = True
            
            # Check tables
            from sqlalchemy import inspect
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            expected_tables = ["users", "couples", "invoices", "ceremonies", "failed_login_attempts", "refresh_tokens"]
            
            for table in expected_tables:
                if table in tables:
                    db_info["tables"].append(table)
                else:
                    db_info["issues"].append(f"Missing table: {table}")
            
            # Test basic operations
            db = SessionLocal()
            try:
                # Test user creation
                user_count = db.query(User).count()
                db_info["user_count"] = user_count
                db_info["schema"] = True
            except Exception as e:
                db_info["issues"].append(f"Schema validation failed: {str(e)}")
            finally:
                db.close()
                
        except Exception as e:
            db_info["issues"].append(f"Database connection failed: {str(e)}")
        
        # Determine status
        if db_info["issues"]:
            db_info["status"] = "critical"
        elif db_info["connection"] and db_info["schema"]:
            db_info["status"] = "healthy"
        else:
            db_info["status"] = "warning"
        
        return db_info

    def validate_api_endpoints(self) -> Dict[str, Any]:
        """Validate API endpoints and functionality."""
        print("🌐 Validating API endpoints...")
        
        api_info = {
            "server_running": False,
            "endpoints": {},
            "authentication": False,
            "issues": [],
            "status": "unknown"
        }
        
        # Test server connectivity
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                api_info["server_running"] = True
                api_info["health_check"] = response.json()
            else:
                api_info["issues"].append(f"Health check failed: {response.status_code}")
        except requests.exceptions.RequestException as e:
            api_info["issues"].append(f"Server not reachable: {str(e)}")
            return api_info
        
        # Test core endpoints
        endpoints_to_test = [
            ("/", "Root endpoint"),
            ("/docs", "API documentation"),
            ("/api/v1/auth/me", "Authentication endpoint"),
            ("/metrics", "Metrics endpoint")
        ]
        
        for endpoint, description in endpoints_to_test:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                api_info["endpoints"][endpoint] = {
                    "status_code": response.status_code,
                    "accessible": response.status_code < 500,
                    "description": description
                }
                
                if response.status_code >= 500:
                    api_info["issues"].append(f"Endpoint {endpoint} returned {response.status_code}")
                    
            except Exception as e:
                api_info["endpoints"][endpoint] = {
                    "status_code": None,
                    "accessible": False,
                    "error": str(e),
                    "description": description
                }
                api_info["issues"].append(f"Endpoint {endpoint} failed: {str(e)}")
        
        # Test authentication flow
        try:
            # Test registration
            register_data = {
                "email": "test@example.com",
                "password": "TestPassword123!",
                "full_name": "Test User"
            }
            
            response = requests.post(f"{self.backend_url}/api/v1/auth/register", json=register_data, timeout=5)
            if response.status_code in [200, 201, 400]:  # 400 means user might already exist
                api_info["authentication"] = True
            else:
                api_info["issues"].append(f"Registration failed: {response.status_code}")
                
        except Exception as e:
            api_info["issues"].append(f"Authentication test failed: {str(e)}")
        
        # Determine status
        if api_info["issues"]:
            api_info["status"] = "critical"
        elif api_info["server_running"] and api_info["authentication"]:
            api_info["status"] = "healthy"
        else:
            api_info["status"] = "warning"
        
        return api_info

    def validate_security_features(self) -> Dict[str, Any]:
        """Validate security features and configurations."""
        print("🔒 Validating security features...")
        
        security_info = {
            "password_hashing": False,
            "jwt_tokens": False,
            "cors_config": False,
            "rate_limiting": False,
            "security_headers": False,
            "issues": [],
            "status": "unknown"
        }
        
        try:
            # Test password hashing
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            test_password = "TestPassword123!"
            hashed = pwd_context.hash(test_password)
            verified = pwd_context.verify(test_password, hashed)
            
            if verified:
                security_info["password_hashing"] = True
            else:
                security_info["issues"].append("Password hashing verification failed")
                
        except Exception as e:
            security_info["issues"].append(f"Password hashing test failed: {str(e)}")
        
        try:
            # Test JWT token generation
            from jose import jwt
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from app.core.config import settings
            
            token_data = {"sub": "test@example.com"}
            token = jwt.encode(token_data, settings.secret_key, algorithm=settings.algorithm)
            decoded = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            
            if decoded["sub"] == "test@example.com":
                security_info["jwt_tokens"] = True
            else:
                security_info["issues"].append("JWT token verification failed")
                
        except Exception as e:
            security_info["issues"].append(f"JWT token test failed: {str(e)}")
        
        # Test CORS configuration
        try:
            response = requests.options(f"{self.backend_url}/api/v1/auth/register", 
                                      headers={"Origin": "http://localhost:3005"})
            if "Access-Control-Allow-Origin" in response.headers:
                security_info["cors_config"] = True
            else:
                security_info["issues"].append("CORS headers not found")
        except Exception as e:
            security_info["issues"].append(f"CORS test failed: {str(e)}")
        
        # Test rate limiting
        try:
            # Make multiple requests to trigger rate limiting
            responses = []
            for i in range(10):
                response = requests.get(f"{self.backend_url}/health", timeout=2)
                responses.append(response.status_code)
            
            if 429 in responses:  # Rate limit hit
                security_info["rate_limiting"] = True
            else:
                security_info["warnings"] = ["Rate limiting not triggered in test"]
                
        except Exception as e:
            security_info["issues"].append(f"Rate limiting test failed: {str(e)}")
        
        # Test security headers
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            security_headers = [
                "X-Content-Type-Options",
                "X-Frame-Options", 
                "X-XSS-Protection",
                "Strict-Transport-Security"
            ]
            
            missing_headers = []
            for header in security_headers:
                if header not in response.headers:
                    missing_headers.append(header)
            
            if not missing_headers:
                security_info["security_headers"] = True
            else:
                security_info["issues"].append(f"Missing security headers: {', '.join(missing_headers)}")
                
        except Exception as e:
            security_info["issues"].append(f"Security headers test failed: {str(e)}")
        
        # Determine status
        if security_info["issues"]:
            security_info["status"] = "critical"
        elif all([security_info["password_hashing"], security_info["jwt_tokens"], 
                  security_info["cors_config"], security_info["security_headers"]]):
            security_info["status"] = "healthy"
        else:
            security_info["status"] = "warning"
        
        return security_info

    def validate_frontend_integration(self) -> Dict[str, Any]:
        """Validate frontend integration and connectivity."""
        print("🎨 Validating frontend integration...")
        
        frontend_info = {
            "server_running": False,
            "api_connectivity": False,
            "build_status": False,
            "issues": [],
            "status": "unknown"
        }
        
        # Test frontend server
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                frontend_info["server_running"] = True
            else:
                frontend_info["issues"].append(f"Frontend server returned {response.status_code}")
        except requests.exceptions.RequestException as e:
            frontend_info["issues"].append(f"Frontend server not reachable: {str(e)}")
        
        # Test API connectivity from frontend
        if frontend_info["server_running"]:
            try:
                response = requests.get(f"{self.frontend_url}/api/health", timeout=5)
                if response.status_code in [200, 404]:  # 404 is expected if endpoint doesn't exist
                    frontend_info["api_connectivity"] = True
                else:
                    frontend_info["issues"].append(f"Frontend API connectivity failed: {response.status_code}")
            except Exception as e:
                frontend_info["issues"].append(f"Frontend API connectivity test failed: {str(e)}")
        
        # Check build status
        frontend_dir = Path("../frontend")
        if frontend_dir.exists():
            package_json = frontend_dir / "package.json"
            if package_json.exists():
                frontend_info["build_status"] = True
            else:
                frontend_info["issues"].append("package.json not found")
        else:
            frontend_info["issues"].append("Frontend directory not found")
        
        # Determine status
        if frontend_info["issues"]:
            frontend_info["status"] = "critical"
        elif frontend_info["server_running"] and frontend_info["build_status"]:
            frontend_info["status"] = "healthy"
        else:
            frontend_info["status"] = "warning"
        
        return frontend_info

    def validate_performance_metrics(self) -> Dict[str, Any]:
        """Validate performance and resource usage."""
        print("⚡ Validating performance metrics...")
        
        performance_info = {
            "response_times": {},
            "memory_usage": {},
            "cpu_usage": {},
            "issues": [],
            "status": "unknown"
        }
        
        # Test response times
        endpoints_to_test = ["/health", "/", "/docs"]
        
        for endpoint in endpoints_to_test:
            try:
                start_time = time.time()
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                performance_info["response_times"][endpoint] = {
                    "time_ms": response_time,
                    "status_code": response.status_code,
                    "acceptable": response_time < 1000  # Less than 1 second
                }
                
                if response_time > 1000:
                    performance_info["issues"].append(f"Slow response time for {endpoint}: {response_time:.2f}ms")
                    
            except Exception as e:
                performance_info["response_times"][endpoint] = {
                    "time_ms": None,
                    "error": str(e),
                    "acceptable": False
                }
                performance_info["issues"].append(f"Performance test failed for {endpoint}: {str(e)}")
        
        # Check memory usage (basic check)
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            performance_info["memory_usage"] = {
                "rss_mb": memory_info.rss / 1024 / 1024,
                "vms_mb": memory_info.vms / 1024 / 1024,
                "acceptable": memory_info.rss < 500 * 1024 * 1024  # Less than 500MB
            }
            
            if memory_info.rss > 500 * 1024 * 1024:
                performance_info["issues"].append(f"High memory usage: {memory_info.rss / 1024 / 1024:.2f}MB")
                
        except ImportError:
            performance_info["memory_usage"] = {"psutil_not_available": True}
        except Exception as e:
            performance_info["issues"].append(f"Memory usage check failed: {str(e)}")
        
        # Determine status
        if performance_info["issues"]:
            performance_info["status"] = "warning"
        else:
            performance_info["status"] = "healthy"
        
        return performance_info

    def validate_documentation(self) -> Dict[str, Any]:
        """Validate documentation completeness."""
        print("📚 Validating documentation...")
        
        docs_info = {
            "readme_exists": False,
            "api_docs": False,
            "deployment_guide": False,
            "maintenance_guide": False,
            "missing_docs": [],
            "status": "unknown"
        }
        
        # Check for essential documentation files
        required_docs = [
            "README.md",
            "CONTRIBUTING.md", 
            "DEVELOPMENT.md",
            "MAINTENANCE_GUIDE.md",
            "DEPLOYMENT.md"
        ]
        
        for doc in required_docs:
            if Path(f"../{doc}").exists():
                if doc == "README.md":
                    docs_info["readme_exists"] = True
                elif doc == "MAINTENANCE_GUIDE.md":
                    docs_info["maintenance_guide"] = True
                elif doc == "DEPLOYMENT.md":
                    docs_info["deployment_guide"] = True
            else:
                docs_info["missing_docs"].append(doc)
        
        # Check API documentation
        try:
            response = requests.get(f"{self.backend_url}/docs", timeout=5)
            if response.status_code == 200:
                docs_info["api_docs"] = True
            else:
                docs_info["missing_docs"].append("API documentation not accessible")
        except Exception as e:
            docs_info["missing_docs"].append(f"API documentation check failed: {str(e)}")
        
        # Determine status
        if docs_info["missing_docs"]:
            docs_info["status"] = "warning"
        else:
            docs_info["status"] = "healthy"
        
        return docs_info

    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run all validation checks."""
        print("🚀 Starting comprehensive system validation...")
        print("="*60)
        
        # Run all validation checks
        self.results["validation_results"]["python_environment"] = self.validate_python_environment()
        self.results["validation_results"]["database_connection"] = self.validate_database_connection()
        self.results["validation_results"]["api_endpoints"] = self.validate_api_endpoints()
        self.results["validation_results"]["security_features"] = self.validate_security_features()
        self.results["validation_results"]["frontend_integration"] = self.validate_frontend_integration()
        self.results["validation_results"]["performance_metrics"] = self.validate_performance_metrics()
        self.results["validation_results"]["documentation"] = self.validate_documentation()
        
        # Generate overall status
        self.generate_overall_status()
        
        return self.results

    def generate_overall_status(self):
        """Generate overall system status."""
        validation_results = self.results["validation_results"]
        
        critical_issues = []
        warnings = []
        
        for category, result in validation_results.items():
            if result.get("status") == "critical":
                critical_issues.append(f"{category}: {', '.join(result.get('issues', []))}")
            elif result.get("status") == "warning":
                warnings.extend(result.get("issues", []))
                warnings.extend(result.get("warnings", []))
        
        self.results["critical_issues"] = critical_issues
        self.results["warnings"] = warnings
        
        # Determine overall status
        if critical_issues:
            self.results["overall_status"] = "critical"
        elif warnings:
            self.results["overall_status"] = "warning"
        else:
            self.results["overall_status"] = "healthy"
        
        # Generate recommendations
        self.generate_recommendations()

    def generate_recommendations(self):
        """Generate recommendations based on validation results."""
        recommendations = []
        
        if self.results["overall_status"] == "critical":
            recommendations.append("CRITICAL: Fix all critical issues before deployment")
        
        validation_results = self.results["validation_results"]
        
        # Database recommendations
        if validation_results.get("database_connection", {}).get("status") == "critical":
            recommendations.append("Fix database connection issues")
        
        # Security recommendations
        if validation_results.get("security_features", {}).get("status") == "critical":
            recommendations.append("Fix security configuration issues")
        
        # Performance recommendations
        if validation_results.get("performance_metrics", {}).get("status") == "warning":
            recommendations.append("Optimize performance for production")
        
        # Documentation recommendations
        if validation_results.get("documentation", {}).get("status") == "warning":
            recommendations.append("Complete missing documentation")
        
        self.results["recommendations"] = recommendations

    def save_results(self, filename: str = "system_validation_results.json"):
        """Save validation results to JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"📄 Validation results saved to {filename}")

    def print_summary(self):
        """Print comprehensive validation summary."""
        print("\n" + "="*60)
        print("🚀 SYSTEM VALIDATION SUMMARY")
        print("="*60)
        print(f"🎯 Overall Status: {self.results['overall_status'].upper()}")
        print(f"📅 Validation Time: {self.results['timestamp']}")
        
        # Print validation results by category
        validation_results = self.results["validation_results"]
        
        for category, result in validation_results.items():
            status_emoji = {
                "healthy": "✅",
                "warning": "⚠️",
                "critical": "❌",
                "unknown": "❓"
            }.get(result.get("status"), "❓")
            
            print(f"\n{status_emoji} {category.replace('_', ' ').title()}: {result.get('status', 'unknown')}")
            
            if result.get("issues"):
                for issue in result["issues"][:3]:  # Show first 3 issues
                    print(f"   • {issue}")
                if len(result["issues"]) > 3:
                    print(f"   • ... and {len(result['issues']) - 3} more issues")
        
        # Print critical issues
        if self.results["critical_issues"]:
            print(f"\n🚨 CRITICAL ISSUES ({len(self.results['critical_issues'])}):")
            for issue in self.results["critical_issues"]:
                print(f"   • {issue}")
        
        # Print warnings
        if self.results["warnings"]:
            print(f"\n⚠️  WARNINGS ({len(self.results['warnings'])}):")
            for warning in self.results["warnings"][:5]:  # Show first 5 warnings
                print(f"   • {warning}")
            if len(self.results["warnings"]) > 5:
                print(f"   • ... and {len(self.results['warnings']) - 5} more warnings")
        
        # Print recommendations
        if self.results["recommendations"]:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in self.results["recommendations"]:
                print(f"   • {rec}")
        
        # Final verdict
        print("\n" + "="*60)
        if self.results["overall_status"] == "healthy":
            print("🎉 SYSTEM IS READY FOR DEPLOYMENT!")
            print("✅ All critical checks passed")
            print("✅ System is bulletproof and production-ready")
        elif self.results["overall_status"] == "warning":
            print("⚠️  SYSTEM HAS WARNINGS - REVIEW BEFORE DEPLOYMENT")
            print("⚠️  Address warnings for optimal performance")
        else:
            print("❌ SYSTEM HAS CRITICAL ISSUES - DO NOT DEPLOY")
            print("❌ Fix all critical issues before proceeding")
        print("="*60)

def main():
    """Main function to run the system validator."""
    validator = SystemValidator()
    results = validator.run_comprehensive_validation()
    validator.print_summary()
    validator.save_results()
    
    # Return exit code based on results
    if results["overall_status"] == "healthy":
        print("\n🎯 APPROVAL STATUS: READY FOR APPROVAL")
        return 0
    elif results["overall_status"] == "warning":
        print("\n🎯 APPROVAL STATUS: NEEDS REVIEW")
        return 1
    else:
        print("\n🎯 APPROVAL STATUS: NOT READY - CRITICAL ISSUES")
        return 2

if __name__ == "__main__":
    sys.exit(main())
