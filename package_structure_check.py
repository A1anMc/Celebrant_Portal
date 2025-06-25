#!/usr/bin/env python3
"""
Final package structure verification for Melbourne Celebrant Portal.
This script verifies that all Python packages and imports are ready for deployment.
"""

import sys
import os
from pathlib import Path

def check_init_files():
    """Check that all required __init__.py files exist."""
    print("🔍 Checking __init__.py files...")
    
    required_init_files = [
        "celebrant-portal-v2/backend/app/__init__.py",
        "celebrant-portal-v2/backend/app/api/__init__.py", 
        "celebrant-portal-v2/backend/app/auth/__init__.py",
        "celebrant-portal-v2/backend/app/models/__init__.py",
        "celebrant-portal-v2/backend/app/schemas/__init__.py",
        "celebrant-portal-v2/backend/app/services/__init__.py",
        "celebrant-portal-v2/backend/app/utils/__init__.py",
    ]
    
    missing_files = []
    for file_path in required_init_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            print(f"❌ Missing: {file_path}")
        else:
            print(f"✅ Found: {file_path}")
    
    return len(missing_files) == 0

def check_critical_imports():
    """Check critical imports for deployment."""
    print("\n🧪 Testing critical imports...")
    
    # Change to backend directory for imports
    backend_path = Path("celebrant-portal-v2/backend")
    if backend_path.exists():
        sys.path.insert(0, str(backend_path.absolute()))
    
    critical_imports = [
        ("app.main", "Main FastAPI application"),
        ("app.config", "Configuration settings"),
        ("app.database", "Database connection"),
        ("app.models.user", "User model"),
        ("app.auth.router", "Authentication router"),
        ("app.api.dashboard", "Dashboard API"),
    ]
    
    failed_imports = []
    for module, description in critical_imports:
        try:
            __import__(module)
            print(f"✅ {description}")
        except Exception as e:
            print(f"❌ {description} - Error: {e}")
            failed_imports.append((module, str(e)))
    
    return len(failed_imports) == 0

def check_app_creation():
    """Test FastAPI app creation."""
    print("\n🚀 Testing FastAPI app creation...")
    
    try:
        from app.main import app
        from fastapi import FastAPI
        
        if isinstance(app, FastAPI):
            print("✅ FastAPI app created successfully")
            print(f"   App title: {app.title}")
            print(f"   App version: {app.version}")
            return True
        else:
            print("❌ App is not a FastAPI instance")
            return False
    except Exception as e:
        print(f"❌ Failed to create FastAPI app: {e}")
        return False

def main():
    """Run complete package structure verification."""
    print("🏗️ Melbourne Celebrant Portal - Package Structure Verification")
    print("=" * 70)
    
    # Check current directory
    current_dir = Path.cwd()
    print(f"Current directory: {current_dir}")
    
    # Run checks
    init_files_ok = check_init_files()
    imports_ok = check_critical_imports()
    app_creation_ok = check_app_creation()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 VERIFICATION SUMMARY:")
    print("=" * 70)
    
    checks = [
        ("__init__.py files", init_files_ok),
        ("Critical imports", imports_ok),
        ("FastAPI app creation", app_creation_ok),
    ]
    
    all_passed = True
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
        if not result:
            all_passed = False
    
    print("-" * 70)
    
    if all_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ Python package structure is ready for deployment!")
        print("\nNext steps:")
        print("1. Set environment variables in Render dashboard")
        print("2. Deploy to Render")
        print("3. Run deployment verification script")
        return 0
    else:
        print("❌ Some checks failed.")
        print("Please fix the issues above before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 