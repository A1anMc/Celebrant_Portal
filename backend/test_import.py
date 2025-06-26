#!/usr/bin/env python3
"""Test script to verify app imports work correctly."""

try:
    from app.main import app
    print("✅ Successfully imported app.main:app")
    print(f"✅ App title: {app.title}")
    print("✅ Ready for deployment!")
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Other error: {e}") 