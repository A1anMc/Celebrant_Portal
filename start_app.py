#!/usr/bin/env python3
"""
Railway startup script for the Celebrant Portal.
This script handles initialization and startup for Railway deployment.
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def ensure_directories():
    """Ensure required directories exist."""
    directories = ['database', 'uploads', 'logs', 'temp']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Ensured directory exists: {directory}")

def main():
    """Main startup function."""
    print("🚀 Starting Celebrant Portal on Railway...")
    
    # Ensure directories exist
    ensure_directories()
    
    # Set environment variables if not set
    if not os.environ.get('FLASK_ENV'):
        os.environ['FLASK_ENV'] = 'production'
        print("✅ Set FLASK_ENV=production")
    
    if not os.environ.get('SECRET_KEY'):
        os.environ['SECRET_KEY'] = 'railway-secret-key-change-in-production'
        print("⚠️  Using default SECRET_KEY - please set a proper one in Railway")
    
    # Import and run the app
    try:
        from app import app, db
        
        # Create database tables
        with app.app_context():
            db.create_all()
            print("✅ Database tables created/verified")
        
        # Get port from environment
        port = int(os.environ.get('PORT', 8085))
        print(f"🌐 Starting server on port {port}")
        
        # Run the app
        app.run(host='0.0.0.0', port=port, debug=False)
        
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 