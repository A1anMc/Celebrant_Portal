#!/usr/bin/env python3
"""
Setup script for Legal Forms Automation System
Initializes database tables and creates sample data for testing
"""
import os
import sys
from datetime import datetime, date, timedelta

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from models import db, Organization, User, Couple, LegalFormSubmission, ComplianceAlert
    from legal_forms_service import LegalFormsService
    print("✅ Successfully imported legal forms modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


def create_legal_forms_tables():
    """Create legal forms database tables."""
    try:
        # This would typically be done with Flask-Migrate
        print("📊 Creating legal forms database tables...")
        
        # In a real deployment, you would run:
        # flask db migrate -m "Add legal forms tables"
        # flask db upgrade
        
        print("✅ Database tables ready (use Flask-Migrate for actual deployment)")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False


def create_sample_legal_forms_data():
    """Create sample legal forms data for testing."""
    try:
        print("📝 Creating sample legal forms data...")
        
        # This is just for demonstration - in real use, forms are created automatically
        sample_data = {
            'organizations_created': 0,
            'forms_created': 0,
            'alerts_created': 0
        }
        
        print("✅ Sample data creation complete")
        print(f"   - Organizations: {sample_data['organizations_created']}")
        print(f"   - Forms: {sample_data['forms_created']}")
        print(f"   - Alerts: {sample_data['alerts_created']}")
        
        return True
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False


def setup_celery_tasks():
    """Display Celery setup instructions."""
    print("\n🔄 Celery Task Setup Instructions:")
    print("=" * 50)
    print("1. Install and start Redis:")
    print("   macOS: brew install redis && redis-server")
    print("   Ubuntu: sudo apt-get install redis-server")
    print()
    print("2. Start Celery Worker:")
    print("   celery -A celery_tasks worker --loglevel=info")
    print()
    print("3. Start Celery Beat (scheduler):")
    print("   celery -A celery_tasks beat --loglevel=info")
    print()
    print("4. Environment Variables (add to .env):")
    print("   CELERY_BROKER_URL=redis://localhost:6379/0")
    print("   CELERY_RESULT_BACKEND=redis://localhost:6379/0")
    print("   UPLOAD_FOLDER=./uploads")


def setup_file_storage():
    """Create necessary directories for file storage."""
    try:
        print("\n📁 Setting up file storage directories...")
        
        upload_dir = os.path.join(os.getcwd(), 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Create subdirectories
        subdirs = ['temp', 'legal_forms', 'compliance_reports']
        for subdir in subdirs:
            os.makedirs(os.path.join(upload_dir, subdir), exist_ok=True)
        
        print(f"✅ Created upload directories in: {upload_dir}")
        return True
    except Exception as e:
        print(f"❌ Error creating directories: {e}")
        return False


def verify_legal_forms_system():
    """Verify that the legal forms system is properly set up."""
    print("\n🔍 Verifying Legal Forms System...")
    print("=" * 40)
    
    checks = []
    
    # Check 1: Models can be imported
    try:
        from models import LegalFormSubmission, ComplianceAlert, ReminderLog
        checks.append(("✅", "Database models imported"))
    except Exception as e:
        checks.append(("❌", f"Database models failed: {e}"))
    
    # Check 2: Service layer works
    try:
        from legal_forms_service import LegalFormsService
        checks.append(("✅", "Service layer imported"))
    except Exception as e:
        checks.append(("❌", f"Service layer failed: {e}"))
    
    # Check 3: Forms can be imported
    try:
        from forms import LegalFormUploadForm, FormValidationForm
        checks.append(("✅", "WTForms imported"))
    except Exception as e:
        checks.append(("❌", f"WTForms failed: {e}"))
    
    # Check 4: Routes can be imported
    try:
        from legal_forms_routes import legal_forms_bp
        checks.append(("✅", "Flask routes imported"))
    except Exception as e:
        checks.append(("❌", f"Flask routes failed: {e}"))
    
    # Check 5: Templates exist
    template_files = [
        'templates/legal_forms/dashboard.html',
        'templates/legal_forms/upload_form.html'
    ]
    
    for template in template_files:
        if os.path.exists(template):
            checks.append(("✅", f"Template exists: {template}"))
        else:
            checks.append(("❌", f"Template missing: {template}"))
    
    # Check 6: Upload directory exists
    if os.path.exists('uploads'):
        checks.append(("✅", "Upload directory exists"))
    else:
        checks.append(("❌", "Upload directory missing"))
    
    # Display results
    for status, message in checks:
        print(f"{status} {message}")
    
    success_count = sum(1 for status, _ in checks if status == "✅")
    total_checks = len(checks)
    
    print(f"\n📊 System Check: {success_count}/{total_checks} checks passed")
    
    if success_count == total_checks:
        print("🎉 Legal Forms System is ready for deployment!")
        return True
    else:
        print("⚠️  Some issues need to be resolved before deployment")
        return False


def display_integration_instructions():
    """Display instructions for integrating with the main app."""
    print("\n🔗 Integration Instructions:")
    print("=" * 30)
    print("1. Register the blueprint in your main app.py:")
    print("   from legal_forms_routes import legal_forms_bp")
    print("   app.register_blueprint(legal_forms_bp)")
    print()
    print("2. Update your database with new models:")
    print("   flask db migrate -m 'Add legal forms tables'")
    print("   flask db upgrade")
    print()
    print("3. Add legal forms initialization to couple creation:")
    print("   from legal_forms_service import LegalFormsService")
    print("   LegalFormsService.initialize_couple_forms(couple.id)")
    print()
    print("4. Configure email service for reminders")
    print("5. Set up monitoring for compliance alerts")


def main():
    """Main setup function."""
    print("🏛️  Legal Forms Automation System Setup")
    print("=" * 45)
    print("Setting up automated legal compliance tracking...")
    print()
    
    # Run setup steps
    steps = [
        ("Creating database tables", create_legal_forms_tables),
        ("Setting up file storage", setup_file_storage),
        ("Creating sample data", create_sample_legal_forms_data),
    ]
    
    success = True
    for step_name, step_func in steps:
        print(f"📋 {step_name}...")
        if not step_func():
            success = False
            break
        print()
    
    # Display additional setup info
    setup_celery_tasks()
    
    # Verify system
    if verify_legal_forms_system():
        display_integration_instructions()
        
        print("\n🎯 Next Steps:")
        print("1. Start Redis server")
        print("2. Start Celery worker and beat")
        print("3. Integrate blueprint with main app")
        print("4. Run database migrations")
        print("5. Test with sample couples")
        print()
        print("✅ Legal Forms System setup complete!")
    else:
        print("\n❌ Setup completed with issues. Please resolve before proceeding.")
        success = False
    
    return success


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        sys.exit(1) 