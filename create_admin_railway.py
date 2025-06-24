#!/usr/bin/env python3
"""
Script to create admin user in Railway database.
"""
import os
import sys
from werkzeug.security import generate_password_hash

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import app and database
from app import app, db
from models import User

def create_admin_user():
    """Create admin user in Railway database."""
    with app.app_context():
        # Check if admin user already exists
        existing_user = User.query.filter_by(email='admin@test.com').first()
        
        if existing_user:
            print("✅ Admin user already exists!")
            return
        
        # Create admin user
        admin_user = User(
            email='admin@test.com',
            password_hash=generate_password_hash('admin123'),
            is_active=True,
            is_admin=True,
            first_name='Admin',
            last_name='User'
        )
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("✅ Admin user created successfully!")
        print("📧 Email: admin@test.com")
        print("🔑 Password: admin123")

if __name__ == '__main__':
    create_admin_user() 