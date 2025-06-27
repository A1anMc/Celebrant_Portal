#!/usr/bin/env python3
"""
Dependency installer for Melbourne Celebrant Portal
Ensures all required packages are installed before starting
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a Python package using pip"""
    print(f"📦 Installing {package}...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def check_and_install_dependencies():
    """Check and install all required dependencies"""
    print("🔍 Checking dependencies...")
    
    # Critical packages that must be available
    critical_packages = [
        "fastapi==0.115.6",
        "uvicorn[standard]==0.32.1", 
        "pydantic==2.10.3",
        "pydantic-settings==2.6.1",
        "sqlalchemy==2.0.36",
        "psycopg2-binary==2.9.10",
        "PyJWT==2.10.1",
        "passlib[bcrypt]==1.7.4",
        "argon2-cffi==23.1.0",
        "python-multipart==0.0.12",
        "python-dateutil==2.8.2",
        "pytz==2023.4",
        "gunicorn==23.0.0"
    ]
    
    failed_packages = []
    
    for package in critical_packages:
        package_name = package.split("==")[0].split("[")[0]
        try:
            __import__(package_name.replace("-", "_"))
            print(f"✅ {package_name} already available")
        except ImportError:
            print(f"❌ {package_name} not found, installing...")
            if not install_package(package):
                failed_packages.append(package)
    
    if failed_packages:
        print(f"❌ Failed to install: {failed_packages}")
        return False
    
    # Test specific imports
    try:
        import passlib
        print(f"✅ passlib version: {passlib.__version__}")
    except ImportError as e:
        print(f"❌ passlib import failed: {e}")
        return False
    
    try:
        from passlib.context import CryptContext
        print("✅ passlib.context imported successfully")
    except ImportError as e:
        print(f"❌ passlib.context import failed: {e}")
        return False
    
    print("🎉 All dependencies verified!")
    return True

if __name__ == "__main__":
    if not check_and_install_dependencies():
        print("❌ Dependency check failed")
        sys.exit(1)
    else:
        print("✅ All dependencies ready!") 