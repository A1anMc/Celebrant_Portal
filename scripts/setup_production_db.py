#!/usr/bin/env python3
"""
Script to set up production database on Railway with PostgreSQL.
This script will:
1. Test database connection
2. Create all tables
3. Create admin user and organization
4. Verify setup
"""

import os
import sys
from werkzeug.security import generate_password_hash

# Add the parent directory to the path so we can import our app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_production_database():
    """Set up the production database with all necessary data."""
    
    print("🚀 Setting up production database...")
    
    try:
        # Import app and database
        from app import app, db
        from models import User, Organization
        
        with app.app_context():
            print("✅ App context created")
            
            # Test database connection
            print("🔍 Testing database connection...")
            try:
                # Try a simple query
                db.engine.execute("SELECT 1")
                print("✅ Database connection successful")
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                return False
            
            # Create all tables
            print("📊 Creating database tables...")
            db.create_all()
            print("✅ All tables created successfully")
            
            # Check if admin organization exists
            print("🏢 Setting up organization...")
            admin_org = Organization.query.filter_by(name="A Melbourne Celebrant").first()
            
            if not admin_org:
                admin_org = Organization(
                    name="A Melbourne Celebrant",
                    description="Professional marriage celebrant services in Melbourne",
                    contact_email="admin@test.com",
                    contact_phone="",
                    address="Melbourne, VIC, Australia",
                    is_active=True
                )
                db.session.add(admin_org)
                db.session.commit()
                print("✅ Created admin organization")
            else:
                print("✅ Admin organization already exists")
            
            # Check if admin user exists
            print("👤 Setting up admin user...")
            admin_user = User.query.filter_by(email="admin@test.com").first()
            
            if not admin_user:
                # Create admin user
                password_hash = generate_password_hash("admin123")
                admin_user = User(
                    email="admin@test.com",
                    username="admin",
                    password_hash=password_hash,
                    first_name="Admin",
                    last_name="User",
                    is_admin=True,
                    is_active=True,
                    organization_id=admin_org.id
                )
                db.session.add(admin_user)
                db.session.commit()
                print("✅ Created admin user")
                print(f"📧 Email: admin@test.com")
                print(f"🔐 Password: admin123")
            else:
                # Update existing admin user password
                admin_user.password_hash = generate_password_hash("admin123")
                admin_user.is_active = True
                admin_user.is_admin = True
                admin_user.organization_id = admin_org.id
                db.session.commit()
                print("✅ Updated existing admin user")
                print(f"📧 Email: admin@test.com")
                print(f"🔐 Password: admin123")
            
            # Verify the setup
            print("🔍 Verifying setup...")
            
            # Check tables exist
            tables = db.engine.table_names()
            expected_tables = ['users', 'organizations', 'couples', 'ceremony_templates']
            
            missing_tables = [table for table in expected_tables if table not in tables]
            if missing_tables:
                print(f"⚠️  Missing tables: {missing_tables}")
            else:
                print("✅ All essential tables exist")
            
            # Test admin user login
            test_user = User.query.filter_by(email="admin@test.com").first()
            if test_user and test_user.check_password("admin123"):
                print("✅ Admin user login test passed")
            else:
                print("❌ Admin user login test failed")
                return False
            
            print("\n🎉 Database setup completed successfully!")
            print("\n📋 Login Details:")
            print("   URL: https://a-melbourne-celebrant-production.up.railway.app")
            print("   Email: admin@test.com")
            print("   Password: admin123")
            
            return True
            
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = setup_production_database()
    sys.exit(0 if success else 1) 