#!/usr/bin/env python3
"""
Final deployment readiness check for Melbourne Celebrant Portal
"""

def check_deployment_readiness():
    print("🚀 Melbourne Celebrant Portal - Deployment Readiness Check")
    print("=" * 70)
    
    # Check 1: Required files exist
    import os
    required_files = [
        'requirements.txt',
        'Procfile', 
        'main.py',
        'celebrant-portal-v2/backend/app/main.py',
        'celebrant-portal-v2/backend/app/config.py'
    ]
    
    print("📁 Checking required files...")
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING!")
            return False
    
    # Check 2: Python imports
    print("\n🐍 Checking Python imports...")
    try:
        import main
        print("✅ Root main.py imports successfully")
        print(f"✅ FastAPI app available: {type(main.app).__name__}")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Check 3: Dependencies
    print("\n📦 Checking key dependencies...")
    try:
        import fastapi, uvicorn, sqlalchemy, psycopg2
        print("✅ All key dependencies available")
    except Exception as e:
        print(f"❌ Dependency missing: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("🎉 DEPLOYMENT READY!")
    print("✅ All files present")
    print("✅ Python package structure correct") 
    print("✅ All imports working")
    print("✅ Dependencies installed")
    print("\n🔧 Render Settings:")
    print("   Root Directory: (blank)")
    print("   Build Command: pip install -r requirements.txt")
    print("   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT")
    return True

if __name__ == "__main__":
    success = check_deployment_readiness()
    exit(0 if success else 1)
