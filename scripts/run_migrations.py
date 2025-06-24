#!/usr/bin/env python3
"""
Database migration script for Legal Forms system
"""
import os
import sys
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

def run_migrations():
    """Run database migrations."""
    print("🗄️  Running Legal Forms Database Migrations")
    print("=" * 50)
    
    try:
        # Import Flask app and database
        from app import app, db
        from models import (
            Organization, User, Couple, LegalFormSubmission, 
            ComplianceAlert, ReminderLog
        )
        
        with app.app_context():
            print("📋 Creating database tables...")
            
            # Create all tables
            db.create_all()
            
            print("✅ Database tables created successfully!")
            
            # Check if we have any existing data
            user_count = User.query.count()
            couple_count = Couple.query.count()
            
            print(f"📊 Current database status:")
            print(f"  • Users: {user_count}")
            print(f"  • Couples: {couple_count}")
            
            # Check if legal forms tables exist and are accessible
            try:
                form_count = LegalFormSubmission.query.count()
                alert_count = ComplianceAlert.query.count()
                log_count = ReminderLog.query.count()
                
                print(f"  • Legal Form Submissions: {form_count}")
                print(f"  • Compliance Alerts: {alert_count}")
                print(f"  • Reminder Logs: {log_count}")
                
                print("\n✅ All legal forms tables are ready!")
                
            except Exception as e:
                print(f"⚠️  Legal forms tables need setup: {e}")
                return False
            
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def initialize_sample_data():
    """Initialize sample data for testing."""
    print("\n🎯 Initializing Sample Data")
    print("=" * 30)
    
    try:
        from app import app, db
        from models import Organization, User, Couple, LegalFormSubmission
        from datetime import date, timedelta
        
        with app.app_context():
            # Check if we already have sample data
            if Organization.query.count() > 0:
                print("📋 Sample data already exists, skipping initialization")
                return True
            
            # Create sample organization
            org = Organization(
                name="Alan McCarthy Celebrant Services",
                description="Professional marriage celebrant services",
                contact_email="alan@celebrant.com",
                contact_phone="0400 123 456",
                address="Melbourne, Victoria, Australia",
                is_active=True
            )
            db.session.add(org)
            db.session.flush()  # Get the ID
            
            # Create sample admin user
            admin_user = User(
                username="admin",
                email="alan@celebrant.com",
                name="Alan McCarthy",
                role="owner",
                organization_id=org.id,
                is_active=True
            )
            admin_user.set_password("admin123")
            db.session.add(admin_user)
            db.session.flush()
            
            # Create sample couple with upcoming ceremony
            ceremony_date = date.today() + timedelta(days=45)  # 45 days from now
            
            couple = Couple(
                organization_id=org.id,
                celebrant_id=admin_user.id,
                partner1_name="Sarah Johnson",
                partner1_email="sarah@example.com",
                partner1_phone="0400 111 222",
                partner2_name="Michael Smith",
                partner2_email="michael@example.com",
                partner2_phone="0400 333 444",
                ceremony_date=ceremony_date,
                ceremony_time="2:00 PM",
                ceremony_location="Royal Botanic Gardens, Melbourne",
                ceremony_type="Civil",
                guest_count=50,
                package="Premium",
                fee=1200.00,
                status="Confirmed"
            )
            db.session.add(couple)
            db.session.flush()
            
            # Create legal form submissions for the couple
            # NOIM form (due 31 days before ceremony)
            noim_form = LegalFormSubmission(
                organization_id=org.id,
                couple_id=couple.id,
                form_type="noim",
                status="not_started"
            )
            noim_form.calculate_deadline(ceremony_date, "noim")
            noim_form.generate_reminder_schedule()
            db.session.add(noim_form)
            
            # Declaration form (due 7 days before ceremony)
            declaration_form = LegalFormSubmission(
                organization_id=org.id,
                couple_id=couple.id,
                form_type="declaration",
                status="not_started"
            )
            declaration_form.calculate_deadline(ceremony_date, "declaration")
            declaration_form.generate_reminder_schedule()
            db.session.add(declaration_form)
            
            db.session.commit()
            
            print("✅ Sample data created successfully!")
            print(f"  • Organization: {org.name}")
            print(f"  • Admin User: {admin_user.username} (password: admin123)")
            print(f"  • Sample Couple: {couple.partner1_name} & {couple.partner2_name}")
            print(f"  • Ceremony Date: {ceremony_date}")
            print(f"  • NOIM Deadline: {noim_form.legal_deadline}")
            print(f"  • Declaration Deadline: {declaration_form.legal_deadline}")
            
            return True
            
    except Exception as e:
        print(f"❌ Sample data initialization failed: {e}")
        db.session.rollback()
        return False

def main():
    """Main migration function."""
    print("🚀 Legal Forms System - Database Setup")
    print("=" * 50)
    
    # Run migrations
    if not run_migrations():
        print("❌ Migration failed, exiting")
        sys.exit(1)
    
    # Ask about sample data
    create_sample = input("\nCreate sample data for testing? (y/N): ").lower().strip() == 'y'
    if create_sample:
        if not initialize_sample_data():
            print("⚠️  Sample data creation failed, but migrations succeeded")
    
    print("\n🎉 Database setup complete!")
    print("\nNext steps:")
    print("1. Start Redis: brew services start redis")
    print("2. Run Celery: python run_celery.py")
    print("3. Start Flask app: python app.py")
    print("4. Visit: http://localhost:8085/legal-forms/dashboard")
    
    if create_sample:
        print("\n👤 Login credentials:")
        print("   Username: admin")
        print("   Password: admin123")

if __name__ == '__main__':
    main() 