#!/usr/bin/env python3
"""
Import test script to verify all Python package imports work correctly.
"""

def test_imports():
    print("🧪 Testing Python Package Structure and Imports...")
    print("=" * 60)
    
    # Test basic imports
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn imported successfully")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False
    
    # Test authentication dependencies
    try:
        import passlib
        print(f"✅ passlib imported successfully - Version: {passlib.__version__}")
    except ImportError as e:
        print(f"❌ passlib not installed: {e}")
        return False
    
    try:
        from passlib.context import CryptContext
        print("✅ passlib.context imported successfully")
    except ImportError as e:
        print(f"❌ passlib.context import failed: {e}")
        return False
    
    try:
        import jwt
        print("✅ PyJWT imported successfully")
    except ImportError as e:
        print(f"❌ PyJWT import failed: {e}")
        return False
    
    try:
        import argon2
        print("✅ argon2-cffi imported successfully")
    except ImportError as e:
        print(f"❌ argon2-cffi import failed: {e}")
        return False
    
    # Test database dependencies
    try:
        import sqlalchemy
        print(f"✅ SQLAlchemy imported successfully - Version: {sqlalchemy.__version__}")
    except ImportError as e:
        print(f"❌ SQLAlchemy import failed: {e}")
        return False
    
    try:
        import psycopg2
        print("✅ psycopg2 imported successfully")
    except ImportError as e:
        print(f"❌ psycopg2 import failed: {e}")
        return False
    
    # Test pydantic
    try:
        import pydantic
        print(f"✅ Pydantic imported successfully - Version: {pydantic.__version__}")
    except ImportError as e:
        print(f"❌ Pydantic import failed: {e}")
        return False
    
    # Test app imports
    try:
        from app.config import settings
        print(f"✅ App config imported - Environment: {settings.environment}")
    except ImportError as e:
        print(f"❌ App config import failed: {e}")
        return False
    
    try:
        from app.main import app
        print(f"✅ FastAPI app imported - Type: {type(app).__name__}")
    except ImportError as e:
        print(f"❌ FastAPI app import failed: {e}")
        return False
    
    print("🎉 ALL IMPORTS SUCCESSFUL!")
    return True

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("✅ DEPLOYMENT READY!")
    else:
        print("❌ Import tests failed - Check dependencies in requirements.txt")
