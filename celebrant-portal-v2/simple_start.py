#!/usr/bin/env python3
"""
Simple start script for Melbourne Celebrant Portal
Direct approach with minimal complexity
"""

import os
import sys
import subprocess

def run_cmd(cmd, description="Running command"):
    """Run a command and print output"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, text=True, capture_output=True)
        print(f"✅ {description} - SUCCESS")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        if e.stdout:
            print(f"   Output: {e.stdout}")
        return False

def main():
    print("🚀 Simple Melbourne Celebrant Portal Startup")
    print("=" * 50)
    
    # Show current environment
    print(f"📍 Current directory: {os.getcwd()}")
    print(f"🐍 Python executable: {sys.executable}")
    print(f"📂 Available files: {os.listdir('.')}")
    
    # Install passlib directly
    print("\n🔧 Installing passlib...")
    if not run_cmd("pip install 'passlib[bcrypt]==1.7.4'", "Installing passlib"):
        print("⚠️  Passlib installation failed, continuing anyway...")
    
    # Test passlib import
    print("\n🧪 Testing passlib import...")
    try:
        import passlib
        print(f"✅ passlib imported successfully - Version: {passlib.__version__}")
    except ImportError as e:
        print(f"❌ passlib import failed: {e}")
        print("🔧 Attempting alternative installation...")
        run_cmd("pip install --force-reinstall 'passlib[bcrypt]==1.7.4'", "Force reinstalling passlib")
        try:
            import passlib
            print(f"✅ passlib imported after reinstall - Version: {passlib.__version__}")
        except ImportError:
            print("❌ passlib still not available")
            sys.exit(1)
    
    # Navigate to backend directory
    backend_dir = None
    if os.path.exists("celebrant-portal-v2/backend/app/main.py"):
        backend_dir = "celebrant-portal-v2/backend"
    elif os.path.exists("backend/app/main.py"):
        backend_dir = "backend"
    
    if not backend_dir:
        print("❌ Could not find backend directory")
        sys.exit(1)
    
    print(f"\n📁 Changing to backend directory: {backend_dir}")
    os.chdir(backend_dir)
    print(f"📍 Now in: {os.getcwd()}")
    
    # Install dependencies in backend directory too
    print("\n🔧 Installing dependencies in backend directory...")
    run_cmd("pip install 'passlib[bcrypt]==1.7.4'", "Installing passlib in backend")
    
    # Test imports
    print("\n🧪 Testing all imports...")
    if not run_cmd("python test_imports.py", "Testing imports"):
        print("❌ Import tests failed")
        sys.exit(1)
    
    # Start the application
    print("\n🌟 Starting FastAPI application...")
    port = os.environ.get("PORT", "8000")
    cmd = f"gunicorn app.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:{port}"
    
    print(f"🚀 Running: {cmd}")
    print(f"🌐 Application will be available on port {port}")
    
    # Run gunicorn directly without subprocess to avoid issues
    os.system(cmd)

if __name__ == "__main__":
    main() 