#!/usr/bin/env python3
"""
Script to update admin user password in Railway MySQL database.
"""

import os
import sys
from werkzeug.security import generate_password_hash
from sqlalchemy import create_engine, text

# Add the parent directory to the path so we can import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

def update_admin_password():
    """Update admin user password in the database."""
    
    # Get database URL from config (which handles the mysql+pymysql conversion)
    env = os.environ.get('FLASK_ENV', 'default')
    database_url = config[env].SQLALCHEMY_DATABASE_URI
    
    if not database_url:
        print("❌ Database URL not found in config")
        return False
    
    try:
        # Create database engine
        engine = create_engine(database_url)
        
        # Generate new password hash
        new_password = "admin123"
        password_hash = generate_password_hash(new_password)
        
        print(f"🔑 Generated password hash for '{new_password}'")
        print(f"📝 Hash: {password_hash}")
        
        # Update the admin user's password
        with engine.connect() as conn:
            # First, check if admin user exists
            result = conn.execute(text("SELECT id, email, is_active FROM users WHERE email = 'admin@test.com'"))
            user = result.fetchone()
            
            if not user:
                print("❌ Admin user (admin@test.com) not found in database")
                return False
            
            print(f"✅ Found admin user: ID={user.id}, Email={user.email}, Active={user.is_active}")
            
            # Update password
            update_result = conn.execute(
                text("UPDATE users SET password_hash = :password_hash WHERE email = 'admin@test.com'"),
                {"password_hash": password_hash}
            )
            
            conn.commit()
            
            print(f"✅ Successfully updated admin password")
            print(f"🔐 New password: {new_password}")
            print(f"📧 Email: admin@test.com")
            
            return True
            
    except Exception as e:
        print(f"❌ Error updating admin password: {e}")
        return False

if __name__ == "__main__":
    success = update_admin_password()
    sys.exit(0 if success else 1) 