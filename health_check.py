#!/usr/bin/env python3
"""
Health Check Script for Celebrant Portal
Verifies database connectivity, models, and critical application functions.
"""

import sys
import os
from datetime import datetime

def health_check():
    """Perform comprehensive health check."""
    print("=" * 60)
    print("🏥 CELEBRANT PORTAL HEALTH CHECK")
    print("=" * 60)
    print(f"⏰ Check time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    issues = []
    checks_passed = 0
    total_checks = 0
    
    # Test 1: Import Flask app
    total_checks += 1
    try:
        from app import app, db
        print("✅ Flask app imports successfully")
        checks_passed += 1
    except Exception as e:
        print(f"❌ Flask app import failed: {e}")
        issues.append("Flask app import failure")
    
    # Test 2: Database connectivity
    total_checks += 1
    try:
        with app.app_context():
            db.engine.connect()
        print("✅ Database connection successful")
        checks_passed += 1
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        issues.append("Database connectivity issue")
    
    # Test 3: Model imports
    total_checks += 1
    try:
        from app import User, Couple, CeremonyTemplate, ImportedName, ImportSession
        print("✅ All models import successfully")
        checks_passed += 1
    except Exception as e:
        print(f"❌ Model import failed: {e}")
        issues.append("Model import failure")
    
    # Test 4: Database tables exist
    total_checks += 1
    try:
        with app.app_context():
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            required_tables = ['users', 'couples', 'ceremony_templates', 'imported_names', 'import_sessions']
            missing_tables = [t for t in required_tables if t not in tables]
            
            if missing_tables:
                print(f"❌ Missing database tables: {', '.join(missing_tables)}")
                issues.append(f"Missing tables: {', '.join(missing_tables)}")
            else:
                print("✅ All required database tables exist")
                checks_passed += 1
    except Exception as e:
        print(f"❌ Database table check failed: {e}")
        issues.append("Database table verification failure")
    
    # Test 5: Critical directories exist
    total_checks += 1
    try:
        required_dirs = ['templates', 'static', 'services']
        missing_dirs = [d for d in required_dirs if not os.path.exists(d)]
        
        if missing_dirs:
            print(f"❌ Missing directories: {', '.join(missing_dirs)}")
            issues.append(f"Missing directories: {', '.join(missing_dirs)}")
        else:
            print("✅ All required directories exist")
            checks_passed += 1
    except Exception as e:
        print(f"❌ Directory check failed: {e}")
        issues.append("Directory check failure")
    
    # Test 6: Template rendering
    total_checks += 1
    try:
        with app.test_request_context():
            from flask import render_template
            render_template('base.html')
        print("✅ Base template renders successfully")
        checks_passed += 1
    except Exception as e:
        print(f"❌ Template rendering failed: {e}")
        issues.append("Template rendering failure")
    
    # Test 7: Configuration check
    total_checks += 1
    try:
        required_configs = ['SECRET_KEY', 'SQLALCHEMY_DATABASE_URI']
        missing_configs = [c for c in required_configs if not app.config.get(c)]
        
        if missing_configs:
            print(f"❌ Missing configurations: {', '.join(missing_configs)}")
            issues.append(f"Missing configurations: {', '.join(missing_configs)}")
        else:
            print("✅ All required configurations present")
            checks_passed += 1
    except Exception as e:
        print(f"❌ Configuration check failed: {e}")
        issues.append("Configuration check failure")
    
    # Summary
    print()
    print("=" * 60)
    print("📊 HEALTH CHECK SUMMARY")
    print("=" * 60)
    print(f"✅ Checks passed: {checks_passed}/{total_checks}")
    
    if issues:
        print("\n🚨 Issues found:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        print()
        print("❌ HEALTH CHECK FAILED")
        return False
    else:
        print("\n🎉 ALL CHECKS PASSED - APPLICATION IS HEALTHY!")
        return True

if __name__ == "__main__":
    success = health_check()
    sys.exit(0 if success else 1) 