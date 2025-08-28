#!/usr/bin/env python3
"""
Dependency Checker for Melbourne Celebrant Portal
Tests all dependencies and identifies potential issues.
"""

import sys
import importlib
import subprocess
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import traceback

class DependencyChecker:
    """Comprehensive dependency checker and health monitor."""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "python_version": sys.version,
            "checks": {},
            "warnings": [],
            "errors": [],
            "recommendations": []
        }
        
        # Core dependencies to test
        self.core_dependencies = [
            "fastapi",
            "uvicorn",
            "sqlalchemy",
            "pydantic",
            "pydantic_settings",
            "jose",  # python-jose
            "passlib",
            "multipart",  # python-multipart
            "email_validator",  # email-validator
            "dotenv",  # python-dotenv
            "starlette",
            "secure",
            "cryptography",
            "bcrypt",
            "httpx",
            "psycopg2",  # psycopg2-binary
            "alembic",
            "gunicorn"
        ]
        
        # Development dependencies
        self.dev_dependencies = [
            "pytest",
            "pytest-asyncio",
            "black",
            "isort",
            "flake8",
            "mypy",
            "pre-commit"
        ]
        
        # Optional dependencies
        self.optional_dependencies = [
            "redis",
            "websockets",
            "structlog"
        ]
        
        # Security-critical dependencies
        self.security_dependencies = [
            "cryptography",
            "bcrypt",
            "jose",  # python-jose
            "passlib"
        ]

    def check_python_version(self) -> Dict[str, Any]:
        """Check Python version compatibility."""
        version_info = {
            "current": sys.version_info,
            "version_string": sys.version,
            "is_compatible": True,
            "recommendations": []
        }
        
        # Check minimum Python version (3.8+)
        if sys.version_info < (3, 8):
            version_info["is_compatible"] = False
            version_info["recommendations"].append("Python 3.8+ required")
        
        # Check for optimal version (3.11+ recommended)
        if sys.version_info < (3, 11):
            version_info["recommendations"].append("Python 3.11+ recommended for best performance")
        
        return version_info

    def test_import(self, module_name: str) -> Dict[str, Any]:
        """Test if a module can be imported successfully."""
        result = {
            "module": module_name,
            "importable": False,
            "version": None,
            "error": None,
            "warning": None
        }
        
        try:
            module = importlib.import_module(module_name)
            result["importable"] = True
            
            # Try to get version
            try:
                if hasattr(module, '__version__'):
                    result["version"] = module.__version__
                elif hasattr(module, 'version'):
                    result["version"] = module.version
            except Exception:
                pass
                
        except ImportError as e:
            result["error"] = str(e)
        except Exception as e:
            result["error"] = str(e)
            result["warning"] = "Unexpected error during import"
        
        return result

    def check_security_dependencies(self) -> Dict[str, Any]:
        """Check security-critical dependencies."""
        security_results = {
            "status": "unknown",
            "checks": {},
            "warnings": [],
            "critical_issues": []
        }
        
        for dep in self.security_dependencies:
            result = self.test_import(dep)
            security_results["checks"][dep] = result
            
            if not result["importable"]:
                security_results["critical_issues"].append(f"Security dependency {dep} not available")
            elif result["error"]:
                security_results["warnings"].append(f"Security dependency {dep} has issues: {result['error']}")
        
        # Determine overall security status
        if security_results["critical_issues"]:
            security_results["status"] = "critical"
        elif security_results["warnings"]:
            security_results["status"] = "warning"
        else:
            security_results["status"] = "secure"
        
        return security_results

    def check_database_dependencies(self) -> Dict[str, Any]:
        """Check database-related dependencies."""
        db_results = {
            "sqlalchemy": self.test_import("sqlalchemy"),
            "psycopg2": self.test_import("psycopg2"),
            "alembic": self.test_import("alembic"),
            "status": "unknown"
        }
        
        # Check if SQLAlchemy is working
        if db_results["sqlalchemy"]["importable"]:
            try:
                from sqlalchemy import create_engine
                from sqlalchemy.orm import sessionmaker
                engine = create_engine("sqlite:///:memory:")
                SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
                db_results["status"] = "working"
            except Exception as e:
                db_results["status"] = "error"
                db_results["error"] = str(e)
        else:
            db_results["status"] = "missing"
        
        return db_results

    def check_web_framework_dependencies(self) -> Dict[str, Any]:
        """Check web framework dependencies."""
        web_results = {
            "fastapi": self.test_import("fastapi"),
            "uvicorn": self.test_import("uvicorn"),
            "starlette": self.test_import("starlette"),
            "status": "unknown"
        }
        
        # Test FastAPI basic functionality
        if web_results["fastapi"]["importable"]:
            try:
                from fastapi import FastAPI
                app = FastAPI()
                web_results["status"] = "working"
            except Exception as e:
                web_results["status"] = "error"
                web_results["error"] = str(e)
        else:
            web_results["status"] = "missing"
        
        return web_results

    def check_validation_dependencies(self) -> Dict[str, Any]:
        """Check validation and serialization dependencies."""
        validation_results = {
            "pydantic": self.test_import("pydantic"),
            "pydantic_settings": self.test_import("pydantic_settings"),
            "email_validator": self.test_import("email_validator"),
            "status": "unknown"
        }
        
        # Test Pydantic functionality
        if validation_results["pydantic"]["importable"]:
            try:
                from pydantic import BaseModel
                class TestModel(BaseModel):
                    name: str
                    age: int
                
                test_data = {"name": "test", "age": 25}
                model = TestModel(**test_data)
                validation_results["status"] = "working"
            except Exception as e:
                validation_results["status"] = "error"
                validation_results["error"] = str(e)
        else:
            validation_results["status"] = "missing"
        
        return validation_results

    def check_authentication_dependencies(self) -> Dict[str, Any]:
        """Check authentication-related dependencies."""
        auth_results = {
            "python_jose": self.test_import("jose"),
            "passlib": self.test_import("passlib"),
            "bcrypt": self.test_import("bcrypt"),
            "cryptography": self.test_import("cryptography"),
            "status": "unknown"
        }
        
        # Test password hashing
        if auth_results["passlib"]["importable"] and auth_results["bcrypt"]["importable"]:
            try:
                from passlib.context import CryptContext
                pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
                hashed = pwd_context.hash("testpassword")
                auth_results["status"] = "working"
            except Exception as e:
                auth_results["status"] = "error"
                auth_results["error"] = str(e)
        else:
            auth_results["status"] = "missing"
        
        return auth_results

    def check_optional_dependencies(self) -> Dict[str, Any]:
        """Check optional dependencies."""
        optional_results = {}
        
        for dep in self.optional_dependencies:
            result = self.test_import(dep)
            optional_results[dep] = result
        
        return optional_results

    def run_comprehensive_check(self) -> Dict[str, Any]:
        """Run all dependency checks."""
        print("🔍 Starting comprehensive dependency check...")
        
        # Check Python version
        self.results["python_version_check"] = self.check_python_version()
        
        # Check core dependencies
        print("📦 Checking core dependencies...")
        for dep in self.core_dependencies:
            self.results["checks"][f"core_{dep}"] = self.test_import(dep)
        
        # Check development dependencies
        print("🛠️  Checking development dependencies...")
        for dep in self.dev_dependencies:
            self.results["checks"][f"dev_{dep}"] = self.test_import(dep)
        
        # Check optional dependencies
        print("⚙️  Checking optional dependencies...")
        self.results["optional_dependencies"] = self.check_optional_dependencies()
        
        # Check security dependencies
        print("🔒 Checking security dependencies...")
        self.results["security_check"] = self.check_security_dependencies()
        
        # Check database dependencies
        print("🗄️  Checking database dependencies...")
        self.results["database_check"] = self.check_database_dependencies()
        
        # Check web framework dependencies
        print("🌐 Checking web framework dependencies...")
        self.results["web_framework_check"] = self.check_web_framework_dependencies()
        
        # Check validation dependencies
        print("✅ Checking validation dependencies...")
        self.results["validation_check"] = self.check_validation_dependencies()
        
        # Check authentication dependencies
        print("🔐 Checking authentication dependencies...")
        self.results["authentication_check"] = self.check_authentication_dependencies()
        
        # Generate summary
        self.generate_summary()
        
        return self.results

    def generate_summary(self):
        """Generate a summary of the check results."""
        total_checks = len(self.results["checks"])
        successful_checks = sum(1 for check in self.results["checks"].values() if check.get("importable", False))
        
        self.results["summary"] = {
            "total_checks": total_checks,
            "successful_checks": successful_checks,
            "failed_checks": total_checks - successful_checks,
            "success_rate": (successful_checks / total_checks * 100) if total_checks > 0 else 0,
            "overall_status": "healthy" if successful_checks == total_checks else "issues_detected"
        }
        
        # Generate recommendations
        self.generate_recommendations()

    def generate_recommendations(self):
        """Generate recommendations based on check results."""
        recommendations = []
        
        # Check for missing critical dependencies
        critical_missing = []
        for name, check in self.results["checks"].items():
            if name.startswith("core_") and not check.get("importable", False):
                dep_name = name.replace("core_", "")
                critical_missing.append(dep_name)
        
        if critical_missing:
            recommendations.append(f"Install missing critical dependencies: {', '.join(critical_missing)}")
        
        # Check security status
        if self.results.get("security_check", {}).get("status") == "critical":
            recommendations.append("Critical security dependencies missing - fix immediately")
        
        # Check Python version
        python_check = self.results.get("python_version_check", {})
        if not python_check.get("is_compatible", True):
            recommendations.append("Upgrade Python to 3.8+ for compatibility")
        
        # Check for outdated packages
        recommendations.append("Run 'pip list --outdated' to check for package updates")
        
        self.results["recommendations"] = recommendations

    def save_results(self, filename: str = "dependency_check_results.json"):
        """Save results to a JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"📄 Results saved to {filename}")

    def print_summary(self):
        """Print a human-readable summary."""
        summary = self.results.get("summary", {})
        
        print("\n" + "="*60)
        print("🔍 DEPENDENCY CHECK SUMMARY")
        print("="*60)
        print(f"✅ Successful checks: {summary.get('successful_checks', 0)}")
        print(f"❌ Failed checks: {summary.get('failed_checks', 0)}")
        print(f"📊 Success rate: {summary.get('success_rate', 0):.1f}%")
        print(f"🎯 Overall status: {summary.get('overall_status', 'unknown')}")
        
        # Print critical issues
        if self.results.get("security_check", {}).get("status") == "critical":
            print("\n🚨 CRITICAL SECURITY ISSUES DETECTED!")
            for issue in self.results["security_check"].get("critical_issues", []):
                print(f"   • {issue}")
        
        # Print recommendations
        if self.results.get("recommendations"):
            print("\n💡 RECOMMENDATIONS:")
            for rec in self.results["recommendations"]:
                print(f"   • {rec}")
        
        print("="*60)

def main():
    """Main function to run the dependency checker."""
    checker = DependencyChecker()
    results = checker.run_comprehensive_check()
    checker.print_summary()
    checker.save_results()
    
    # Return exit code based on results
    if results["summary"]["overall_status"] == "healthy":
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())
