#!/usr/bin/env python3
"""
Script to check and fix admin user in Railway database.
"""
import os
import sys
from werkzeug.security import generate_password_hash, check_password_hash

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import app and database
from app import app, db
from models import User, Organization

def fix_admin_user():
    """Check and fix admin user in Railway database."""
    with app.app_context():
        # First, ensure we have an organization
        organization = Organization.query.filter_by(name='Test Organization').first()
        if not organization:
            print("❌ Organization not found! Creating new one...")
            organization = Organization(
                name='Test Organization',
                slug='test-org',
                contact_email='admin@test.com',
                is_active=True
            )
            db.session.add(organization)
            db.session.commit()
            print("✅ Organization created!")
        else:
            print("✅ Organization found!")
        
        # Find admin user
        admin_user = User.query.filter_by(email='admin@test.com').first()
        
        if not admin_user:
            print("❌ Admin user not found! Creating new one...")
            admin_user = User(
                username='admin',
                email='admin@test.com',
                password_hash=generate_password_hash('admin123'),
                name='Admin User',
                is_active=True,
                is_admin=True,
                role='admin',
                organization_id=organization.id
            )
            db.session.add(admin_user)
        else:
            print("✅ Admin user found!")
            print(f"📧 Email: {admin_user.email}")
            print(f"🔑 Is Active: {admin_user.is_active}")
            print(f"👑 Is Admin: {admin_user.is_admin}")
            
            # Check if password is correct
            if check_password_hash(admin_user.password_hash, 'admin123'):
                print("✅ Password is correct!")
            else:
                print("❌ Password is incorrect! Updating...")
                admin_user.password_hash = generate_password_hash('admin123')
            
            # Ensure user is active and admin
            admin_user.is_active = True
            admin_user.is_admin = True
            admin_user.role = 'admin'
        
        db.session.commit()
        print("✅ Admin user updated successfully!")
        print("📧 Email: admin@test.com")
        print("🔑 Password: admin123")

if __name__ == '__main__':
    fix_admin_user() 