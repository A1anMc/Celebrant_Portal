#!/usr/bin/env python3
"""Simple import test"""

try:
    import fastapi
    print("✅ FastAPI OK")
except ImportError:
    print("❌ FastAPI failed")
    exit(1)

try:
    import passlib
    print(f"✅ passlib OK - Version: {passlib.__version__}")
except ImportError:
    print("❌ passlib failed")
    exit(1)

try:
    from app.main import app
    print("✅ App import OK")
except ImportError as e:
    print(f"❌ App import failed: {e}")
    exit(1)

print("🎉 All imports successful!")
