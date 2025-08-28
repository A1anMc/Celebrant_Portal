#!/usr/bin/env python3
"""
Render Deployment Fix Script
Diagnoses and fixes common Render deployment issues.
"""

import os
import sys
import subprocess
import json
from typing import Dict, List

def check_environment_variables() -> Dict[str, bool]:
    """Check if all required environment variables are set."""
    required_vars = {
        "DATABASE_URL": False,
        "SECRET_KEY": False,
        "ALLOWED_ORIGINS": False,
        "ENVIRONMENT": False,
        "DEBUG": False
    }
    
    for var in required_vars.keys():
        if os.getenv(var):
            required_vars[var] = True
    
    return required_vars

def check_python_version() -> str:
    """Check Python version compatibility."""
    version = sys.version_info
    return f"{version.major}.{version.minor}.{version.micro}"

def check_dependencies() -> Dict[str, bool]:
    """Check if all required dependencies are available."""
    dependencies = {
        "fastapi": False,
        "uvicorn": False,
        "sqlalchemy": False,
        "pydantic": False,
        "pydantic-settings": False,
        "python-dotenv": False,
        "requests": False
    }
    
    for dep in dependencies.keys():
        try:
            __import__(dep.replace("-", "_"))
            dependencies[dep] = True
        except ImportError:
            pass
    
    return dependencies

def generate_render_environment_template() -> str:
    """Generate a template for Render environment variables."""
    template = """# Render Environment Variables Template
# Copy these to your Render dashboard environment variables

# Database Configuration
DATABASE_URL=postgresql://username:password@host:port/database_name

# Security
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration (comma-separated)
ALLOWED_ORIGINS=https://celebrant-portal-ah8ssgciz-alans-projects-baf4c067.vercel.app,http://localhost:3000

# Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# Render Specific
PORT=8000
HOST=0.0.0.0

# Optional: CSRF Protection
CSRF_TOKEN_SECRET=your-csrf-secret-key-here
"""
    return template

def check_app_import() -> bool:
    """Check if the main app can be imported successfully."""
    try:
        from app.main import app
        return True
    except Exception as e:
        print(f"❌ App import failed: {e}")
        return False

def main():
    """Main diagnostic function."""
    print("🔍 Render Deployment Diagnostic")
    print("=" * 50)
    
    # Check Python version
    python_version = check_python_version()
    print(f"🐍 Python Version: {python_version}")
    
    # Check environment variables
    env_vars = check_environment_variables()
    print("\n🔧 Environment Variables:")
    for var, is_set in env_vars.items():
        status = "✅" if is_set else "❌"
        print(f"  {status} {var}")
    
    # Check dependencies
    deps = check_dependencies()
    print("\n📦 Dependencies:")
    for dep, is_available in deps.items():
        status = "✅" if is_available else "❌"
        print(f"  {status} {dep}")
    
    # Check app import
    app_import = check_app_import()
    print(f"\n🚀 App Import: {'✅ Success' if app_import else '❌ Failed'}")
    
    # Generate recommendations
    print("\n💡 Recommendations:")
    
    missing_env_vars = [var for var, is_set in env_vars.items() if not is_set]
    if missing_env_vars:
        print(f"  ❌ Missing environment variables: {', '.join(missing_env_vars)}")
        print("  📝 Generate environment template:")
        print(generate_render_environment_template())
    
    missing_deps = [dep for dep, is_available in deps.items() if not is_available]
    if missing_deps:
        print(f"  ❌ Missing dependencies: {', '.join(missing_deps)}")
        print("  📦 Run: pip install -r requirements.txt")
    
    if not app_import:
        print("  ❌ App import failed - check for syntax errors or missing modules")
    
    # Overall status
    all_good = all(env_vars.values()) and all(deps.values()) and app_import
    print(f"\n🎯 Overall Status: {'✅ READY FOR DEPLOYMENT' if all_good else '❌ ISSUES FOUND'}")

if __name__ == "__main__":
    main()
