#!/usr/bin/env python3
"""
Backend Setup Script for Melbourne Celebrant Portal
Sets up the FastAPI backend with sample data for development.
"""

import os
import sys
from datetime import datetime, date, timedelta

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def setup_backend():
    """Main setup function."""
    print("🚀 Setting up Melbourne Celebrant Portal Backend...")
    
    try:
        from app.database import SessionLocal, create_tables
        from app.models.user import User
        from app.models.couple import Couple
        from app.auth.utils import get_password_hash
        
        # Create database tables
        print("📋 Creating database tables...")
        create_tables()
        
        # Create session
        db = SessionLocal()
        
        # Create admin user
        print("👤 Creating admin user...")
        existing_user = db.query(User).filter(User.email == "admin@celebrant.com").first()
        if not existing_user:
            admin_user = User(
                email="admin@celebrant.com",
                password_hash=get_password_hash("admin123"),
                name="Melbourne Celebrant",
                role="celebrant",
                is_active=True,
                is_verified=True,
                business_name="Melbourne Celebrant Services",
                phone="+61 400 123 456",
                timezone="Australia/Melbourne",
                currency="AUD"
            )
            db.add(admin_user)
            print("   ✓ Created admin user: admin@celebrant.com")
        else:
            print("   Admin user already exists")
        
        db.commit()
        print("✅ Backend setup completed successfully!")
        
        print("\n🎉 Your FastAPI backend is ready!")
        print("\n🔑 Login Credentials:")
        print("   Email: admin@celebrant.com")
        print("   Password: admin123")
        
        print("\n🚀 Next Steps:")
        print("1. Start the server: uvicorn app.main:app --reload --port 8000")
        print("2. View API docs: http://localhost:8000/docs")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False
    
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    setup_backend()
