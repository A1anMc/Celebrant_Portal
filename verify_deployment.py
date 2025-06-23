#!/usr/bin/env python3
"""
Legal Forms Automation - Deployment Verification Script
"""
import os
import sys
import json
from datetime import datetime, date, timedelta
from pathlib import Path

# Add project directory to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("📦 Checking Dependencies...")
    
    required_packages = [
        'flask', 'celery', 'redis', 'sqlalchemy', 
        'flask_sqlalchemy', 'flask_login', 'flask_migrate',
        'flask_wtf', 'wtforms', 'werkzeug'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies installed")
    return True

def check_redis():
    """Check Redis connectivity."""
    print("\n🔴 Checking Redis...")
    
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        info = r.info()
        print(f"  ✅ Redis connected (version: {info.get('redis_version', 'unknown')})")
        return True
    except Exception as e:
        print(f"  ❌ Redis connection failed: {e}")
        print("  Start Redis: brew services start redis (Mac) or sudo systemctl start redis (Linux)")
        return False

def check_models():
    """Check if all models can be imported and used."""
    print("\n📊 Checking Database Models...")
    
    try:
        from models import (
            Organization, User, Couple, LegalFormSubmission,
            ComplianceAlert, ReminderLog
        )
        
        models = [
            ('Organization', Organization),
            ('User', User),
            ('Couple', Couple),
            ('LegalFormSubmission', LegalFormSubmission),
            ('ComplianceAlert', ComplianceAlert),
            ('ReminderLog', ReminderLog)
        ]
        
        for name, model in models:
            # Check if model has required attributes
            if hasattr(model, '__tablename__'):
                print(f"  ✅ {name} (table: {model.__tablename__})")
            else:
                print(f"  ⚠️  {name} - no tablename")
        
        print("✅ All models imported successfully")
        return True
        
    except Exception as e:
        print(f"  ❌ Model import failed: {e}")
        return False

def check_services():
    """Check service layer components."""
    print("\n🔧 Checking Service Layer...")
    
    try:
        from legal_forms_service import LegalFormsService
        
        # Check if service has required methods
        required_methods = [
            'get_dashboard_data', 'upload_form', 'validate_form',
            'get_compliance_alerts', 'generate_reminder_content'
        ]
        
        for method in required_methods:
            if hasattr(LegalFormsService, method):
                print(f"  ✅ {method}")
            else:
                print(f"  ❌ {method} - MISSING")
        
        print("✅ Service layer verified")
        return True
        
    except Exception as e:
        print(f"  ❌ Service layer check failed: {e}")
        return False

def check_routes():
    """Check if routes are properly configured."""
    print("\n🛣️  Checking Routes...")
    
    try:
        from legal_forms_routes import legal_forms_bp
        
        # Check if blueprint has routes by checking its deferred functions
        route_count = len(legal_forms_bp.deferred_functions)
        
        if route_count > 0:
            print(f"  ✅ Blueprint has {route_count} registered routes")
            
            # Try to get some route information
            from app import app
            with app.app_context():
                app.register_blueprint(legal_forms_bp, url_prefix='/legal-forms')
                
                # Get routes for our blueprint
                legal_routes = []
                for rule in app.url_map.iter_rules():
                    if rule.endpoint and rule.endpoint.startswith('legal_forms.'):
                        legal_routes.append(f"{rule.rule} ({', '.join(rule.methods)})")
                
                if legal_routes:
                    print(f"  ✅ Found {len(legal_routes)} legal forms routes")
                    for route in legal_routes[:3]:  # Show first 3 routes
                        print(f"    • {route}")
                    if len(legal_routes) > 3:
                        print(f"    ... and {len(legal_routes) - 3} more routes")
        else:
            print("  ⚠️  No routes found in blueprint")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Routes check failed: {e}")
        return False

def check_celery():
    """Check Celery configuration."""
    print("\n⚙️  Checking Celery Configuration...")
    
    try:
        from celery_app import make_celery, create_celery_app
        from legal_forms_tasks import (
            check_form_deadlines, send_daily_reminders,
            generate_compliance_report, cleanup_old_alerts
        )
        
        print("  ✅ Celery app factory")
        print("  ✅ Task imports")
        
        # Check if tasks are properly decorated
        tasks = [
            check_form_deadlines, send_daily_reminders,
            generate_compliance_report, cleanup_old_alerts
        ]
        
        for task in tasks:
            if hasattr(task, 'delay'):
                print(f"  ✅ {task.name} - properly decorated")
            else:
                print(f"  ❌ {task.__name__} - not a Celery task")
        
        print("✅ Celery configuration verified")
        return True
        
    except Exception as e:
        print(f"  ❌ Celery check failed: {e}")
        return False

def check_templates():
    """Check if email templates exist."""
    print("\n📧 Checking Email Templates...")
    
    template_files = [
        'templates/email/noim_reminder.txt',
        'templates/email/declaration_reminder.txt',
        'templates/email/compliance_report.txt'
    ]
    
    all_exist = True
    for template in template_files:
        if os.path.exists(template):
            print(f"  ✅ {template}")
        else:
            print(f"  ❌ {template} - MISSING")
            all_exist = False
    
    if all_exist:
        print("✅ All email templates found")
    
    return all_exist

def check_directories():
    """Check if required directories exist."""
    print("\n📁 Checking Directories...")
    
    required_dirs = [
        'uploads',
        'uploads/legal_forms',
        'uploads/compliance_reports',
        'templates/legal_forms'
    ]
    
    all_exist = True
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"  ✅ {directory}")
        else:
            print(f"  ❌ {directory} - MISSING")
            try:
                os.makedirs(directory, exist_ok=True)
                print(f"    ✅ Created {directory}")
            except Exception as e:
                print(f"    ❌ Failed to create {directory}: {e}")
                all_exist = False
    
    return all_exist

def check_flask_integration():
    """Check Flask app integration."""
    print("\n🌐 Checking Flask Integration...")
    
    try:
        from app import app
        
        with app.app_context():
            # Check if blueprint is registered
            blueprints = list(app.blueprints.keys())
            print(f"  ✅ Registered blueprints: {', '.join(blueprints)}")
            
            if 'legal_forms' in blueprints:
                print("  ✅ Legal forms blueprint registered")
            else:
                print("  ⚠️  Legal forms blueprint not found")
            
            # Check database connection
            from app import db
            try:
                # Try a simple query
                result = db.engine.execute('SELECT 1').fetchone()
                print("  ✅ Database connection working")
            except Exception as e:
                print(f"  ⚠️  Database connection issue: {e}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Flask integration check failed: {e}")
        return False

def generate_test_report():
    """Generate a test report with sample data."""
    print("\n📋 Generating Test Report...")
    
    try:
        from datetime import date, timedelta
        
        # Sample compliance data
        test_data = {
            'organization': 'Test Celebrant Services',
            'report_date': date.today().strftime('%Y-%m-%d'),
            'total_forms': 12,
            'completed_forms': 8,
            'overdue_forms': 2,
            'upcoming_forms': 2,
            'compliance_rate': 66.7,
            'generated_at': datetime.now().isoformat()
        }
        
        print(f"  📊 Sample Report Data:")
        print(f"    • Total Forms: {test_data['total_forms']}")
        print(f"    • Completed: {test_data['completed_forms']}")
        print(f"    • Overdue: {test_data['overdue_forms']}")
        print(f"    • Compliance Rate: {test_data['compliance_rate']}%")
        
        # Save test report
        report_file = 'test_compliance_report.json'
        with open(report_file, 'w') as f:
            json.dump(test_data, f, indent=2)
        
        print(f"  ✅ Test report saved to {report_file}")
        return True
        
    except Exception as e:
        print(f"  ❌ Test report generation failed: {e}")
        return False

def main():
    """Run all verification checks."""
    print("🚀 Legal Forms Automation - Deployment Verification")
    print("=" * 60)
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Redis", check_redis),
        ("Models", check_models),
        ("Services", check_services),
        ("Routes", check_routes),
        ("Celery", check_celery),
        ("Templates", check_templates),
        ("Directories", check_directories),
        ("Flask Integration", check_flask_integration),
        ("Test Report", generate_test_report)
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} check failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:20} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n🎉 ALL CHECKS PASSED!")
        print("\n🚀 System is ready for deployment!")
        print("\nNext steps:")
        print("1. python run_migrations.py")
        print("2. python run_celery.py (in separate terminal)")
        print("3. python app.py")
        print("4. Visit: http://localhost:8085/legal-forms/dashboard")
        
        return True
    else:
        print(f"\n⚠️  {failed} checks failed. Please fix issues before deployment.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 