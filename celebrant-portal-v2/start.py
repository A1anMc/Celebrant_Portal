#!/usr/bin/env python3
"""
Start script for Melbourne Celebrant Portal
Handles directory navigation, dependency installation, and application startup
"""

import os
import sys
import subprocess

def main():
    print("🚀 Starting Melbourne Celebrant Portal...")
    print(f"📍 Current directory: {os.getcwd()}")
    print(f"🐍 Python executable: {sys.executable}")
    print(f"📂 Directory contents: {os.listdir('.')}")
    
    # First, ensure all dependencies are installed
    print("🔧 Ensuring dependencies are installed...")
    try:
        subprocess.run([sys.executable, "ensure_deps.py"], check=True)
        print("✅ Dependencies verified")
    except subprocess.CalledProcessError:
        print("❌ Dependency installation failed")
        sys.exit(1)
    except FileNotFoundError:
        print("⚠️  ensure_deps.py not found, skipping dependency check")
    
    # Determine the correct backend directory
    if os.path.exists("backend/app/main.py"):
        backend_dir = "backend"
    elif os.path.exists("celebrant-portal-v2/backend/app/main.py"):
        backend_dir = "celebrant-portal-v2/backend"
    else:
        print("❌ Could not find backend directory")
        print("Available directories:", [d for d in os.listdir('.') if os.path.isdir(d)])
        sys.exit(1)
    
    print(f"📁 Using backend directory: {backend_dir}")
    
    # Change to backend directory
    os.chdir(backend_dir)
    print(f"📍 Changed to directory: {os.getcwd()}")
    
    # Test imports first
    print("🧪 Testing imports...")
    try:
        result = subprocess.run([sys.executable, "test_imports.py"], check=True, capture_output=True, text=True)
        print("✅ All imports successful")
        # Only print first few lines to avoid spam
        lines = result.stdout.split('\n')[:5]
        for line in lines:
            if line.strip():
                print(f"   {line}")
    except subprocess.CalledProcessError as e:
        print("❌ Import test failed")
        print(f"Error: {e.stderr}")
        
        # Try one more time with explicit passlib installation
        print("🔧 Installing passlib as fallback...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "passlib[bcrypt]==1.7.4"], check=True)
            subprocess.run([sys.executable, "test_imports.py"], check=True)
            print("✅ Import test successful after passlib installation")
        except subprocess.CalledProcessError:
            print("❌ Import test still failing after passlib installation")
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
    
    print(f"🚀 Running command: {' '.join(cmd)}")
    print(f"🌐 Application will be available on port {port}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main() 