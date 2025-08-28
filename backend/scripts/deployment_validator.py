#!/usr/bin/env python3
"""
Deployment Validation Script
Validates that the application is ready for production deployment.
"""

import sys
import os
import subprocess
import importlib
from pathlib import Path
from typing import List, Dict, Any

def run_command(command: str, cwd: str = None) -> tuple:
    """Run a command and return (success, output)."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def check_python_version() -> bool:
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python version {version.major}.{version.minor}.{version.micro} is not compatible (requires 3.11+)")
        return False

def check_dependencies() -> bool:
    """Check if all required dependencies are installed."""
    required_packages = [
        'fastapi', 'uvicorn', 'sqlalchemy', 'pydantic', 
        'python-jose', 'passlib', 'python-multipart',
        'email-validator', 'python-dotenv', 'psycopg2-binary',
        'alembic', 'gunicorn'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def check_database_migrations() -> bool:
    """Check if database migrations are up to date."""
    success, output = run_command("alembic current")
    if success:
        print("✅ Database migrations are up to date")
        return True
    else:
        print(f"❌ Database migration check failed: {output}")
        return False

def check_security_config() -> bool:
    """Check security configuration."""
    issues = []
    
    # Check if secret key is set
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key or secret_key == 'your-secret-key-here':
        issues.append("SECRET_KEY not properly configured")
    
    # Check if debug is disabled in production
    debug = os.getenv('DEBUG', 'true').lower()
    if debug == 'true':
        issues.append("DEBUG should be false in production")
    
    # Check CORS configuration
    allowed_origins = os.getenv('ALLOWED_ORIGINS')
    if not allowed_origins:
        issues.append("ALLOWED_ORIGINS not configured")
    
    if issues:
        for issue in issues:
            print(f"❌ {issue}")
        return False
    
    print("✅ Security configuration is properly set")
    return True

def check_environment_variables() -> bool:
    """Check required environment variables."""
    required_vars = [
        'DATABASE_URL', 'SECRET_KEY', 'ALGORITHM', 
        'ACCESS_TOKEN_EXPIRE_MINUTES', 'ENVIRONMENT'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        for var in missing_vars:
            print(f"❌ Required environment variable {var} is not set")
        return False
    
    print("✅ All required environment variables are set")
    return True

def run_tests() -> bool:
    """Run the test suite."""
    print("Running tests...")
    success, output = run_command("python -m pytest tests/ -v --tb=short")
    
    if success:
        print("✅ All tests passed")
        return True
    else:
        print(f"❌ Tests failed: {output}")
        return False

def check_code_quality() -> bool:
    """Check code quality with linting tools."""
    issues = []
    
    # Run black check
    success, output = run_command("black --check .")
    if not success:
        issues.append("Code formatting issues (run 'black .' to fix)")
    
    # Run flake8
    success, output = run_command("flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics")
    if not success:
        issues.append("Code quality issues found")
    
    # Run mypy
    success, output = run_command("mypy . --ignore-missing-imports")
    if not success:
        issues.append("Type checking issues found")
    
    if issues:
        for issue in issues:
            print(f"❌ {issue}")
        return False
    
    print("✅ Code quality checks passed")
    return True

def check_docker_build() -> bool:
    """Check if Docker build works."""
    print("Testing Docker build...")
    success, output = run_command("docker build -t test-build .")
    
    if success:
        print("✅ Docker build successful")
        # Clean up test image
        run_command("docker rmi test-build")
        return True
    else:
        print(f"❌ Docker build failed: {output}")
        return False

def main():
    """Main validation function."""
    print("🚀 Melbourne Celebrant Portal - Deployment Validation")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Environment Variables", check_environment_variables),
        ("Security Configuration", check_security_config),
        ("Code Quality", check_code_quality),
        ("Database Migrations", check_database_migrations),
        ("Tests", run_tests),
        ("Docker Build", check_docker_build),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n🔍 Checking {name}...")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error checking {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("📊 Validation Results:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:<25} {status}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All checks passed! Application is ready for deployment.")
        return 0
    else:
        print("⚠️  Some checks failed. Please fix the issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
