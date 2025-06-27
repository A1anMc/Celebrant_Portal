#!/usr/bin/env python3
"""
Start script for Melbourne Celebrant Portal
Handles directory navigation and application startup
"""

import os
import sys
import subprocess

def main():
    print("🚀 Starting Melbourne Celebrant Portal...")
    
    # Determine the correct backend directory
    if os.path.exists("backend/app/main.py"):
        backend_dir = "backend"
    elif os.path.exists("celebrant-portal-v2/backend/app/main.py"):
        backend_dir = "celebrant-portal-v2/backend"
    else:
        print("❌ Could not find backend directory")
        sys.exit(1)
    
    print(f"📁 Using backend directory: {backend_dir}")
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Test imports first
    print("🧪 Testing imports...")
    try:
        subprocess.run([sys.executable, "test_imports.py"], check=True)
        print("✅ All imports successful")
    except subprocess.CalledProcessError:
        print("❌ Import test failed")
        sys.exit(1)
    
    # Start the application
    print("🌟 Starting FastAPI application...")
    port = os.environ.get("PORT", "8000")
    
    cmd = [
        "gunicorn", 
        "app.main:app",
        "-w", "2",
        "-k", "uvicorn.workers.UvicornWorker",
        "--bind", f"0.0.0.0:{port}"
    ]
    
    subprocess.run(cmd)

if __name__ == "__main__":
    main() 