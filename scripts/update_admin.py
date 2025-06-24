#!/usr/bin/env python3
"""
Update Admin Login Details
This script allows you to update the admin user's login credentials.
"""

import os
import sys
from getpass import getpass
from app import app, db, User

def update_admin_credentials():
    """Update admin user credentials interactively."""
    
    print("🔐 Update Admin Login Details")
    print("=" * 40)
    
    with app.app_context():
        # Find existing admin user
        current_admin = User.query.filter_by(is_admin=True).first()
        
        if current_admin:
            print(f"Current admin user: {current_admin.email}")
            print(f"Current name: {current_admin.name}")
        else:
            print("No admin user found. This will create a new admin user.")
        
        print("\nEnter new admin details (press Enter to keep current values):")
        
        # Get new email
        new_email = input(f"Email [{current_admin.email if current_admin else 'admin@celebrant.local'}]: ").strip()
        if not new_email:
            new_email = current_admin.email if current_admin else 'admin@celebrant.local'
        
        # Get new name
        new_name = input(f"Name [{current_admin.name if current_admin else 'Admin User'}]: ").strip()
        if not new_name:
            new_name = current_admin.name if current_admin else 'Admin User'
        
        # Get new password
        print("\nPassword (leave empty to keep current password):")
        new_password = getpass("New password: ")
        if new_password:
            confirm_password = getpass("Confirm password: ")
            if new_password != confirm_password:
                print("❌ Passwords don't match!")
                return False
        
        # Update or create admin user
        if current_admin:
            # Update existing admin
            current_admin.email = new_email
            current_admin.name = new_name
            if new_password:
                current_admin.set_password(new_password)
            
            db.session.commit()
            print("✅ Admin user updated successfully!")
        else:
            # Create new admin
            if not new_password:
                new_password = 'admin123'  # Default password
                print("⚠️  Using default password: admin123")
            
            admin = User(
                username='admin',
                email=new_email,
                name=new_name,
                is_admin=True
            )
            admin.set_password(new_password)
            
            db.session.add(admin)
            db.session.commit()
            print("✅ New admin user created successfully!")
        
        print("\n📋 Updated Login Details:")
        print(f"Email: {new_email}")
        if new_password:
            print(f"Password: {'*' * len(new_password)}")
        print(f"Name: {new_name}")
        
        print("\n🚀 You can now login at: http://localhost:8085/login")
        
        return True

def set_environment_variables():
    """Show how to set environment variables for automated setup."""
    print("\n🔧 Alternative: Set Environment Variables")
    print("=" * 40)
    print("You can also set these environment variables and run setup_database.py:")
    print()
    print("export ADMIN_EMAIL='your-email@domain.com'")
    print("export ADMIN_PASSWORD='your-secure-password'")
    print("export ADMIN_NAME='Your Name'")
    print()
    print("Then run: python setup_database.py")

if __name__ == '__main__':
    try:
        if update_admin_credentials():
            set_environment_variables()
    except KeyboardInterrupt:
        print("\n\n❌ Update cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error updating admin credentials: {str(e)}")
        sys.exit(1) 