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
        print("❌ Import tests failed")
