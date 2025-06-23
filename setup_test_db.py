#!/usr/bin/env python3
"""
Simple database setup script for testing the invoice system.
"""
import os
import sys
from datetime import datetime, date, timedelta
from flask import Flask
from werkzeug.security import generate_password_hash

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import models and app
from models import db, User, Organization, Couple, Invoice
from config import config

# Create Flask app
app = Flask(__name__)
env = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Initialize database
db.init_app(app)

def setup_database():
    """Set up the database with test data."""
    with app.app_context():
        # Create tables
        db.create_all()
        print("✅ Database tables created")
        
        # Create default organization
        org = Organization.query.filter_by(name='Test Organization').first()
        if not org:
            org = Organization(
                name='Test Organization',
                slug='test-org',
                contact_name='Test Admin',
                contact_email='admin@test.com',
                subscription_plan='premium',
                max_users=10,
                max_couples=100,
                max_templates=50
            )
            db.session.add(org)
            db.session.commit()
            print("✅ Test organization created")
        else:
            print("✅ Test organization already exists")
        
        # Create admin user
        admin = User.query.filter_by(email='admin@test.com').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@test.com',
                name='Test Admin',
                role='owner',
                is_admin=True,
                is_active=True,
                organization_id=org.id
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created (admin@test.com / admin123)")
        else:
            print("✅ Admin user already exists")
        
        # Create test couples
        test_couples = [
            {
                'partner1_name': 'John Smith',
                'partner1_email': 'john@test.com',
                'partner1_phone': '0400 123 456',
                'partner2_name': 'Jane Doe',
                'partner2_email': 'jane@test.com',
                'partner2_phone': '0400 654 321',
                'ceremony_date': date.today() + timedelta(days=30),
                'ceremony_location': 'Melbourne Town Hall',
                'status': 'Confirmed',
                'fee': 1200.0,
                'travel_fee': 50.0
            },
            {
                'partner1_name': 'Mike Johnson',
                'partner1_email': 'mike@test.com',
                'partner1_phone': '0400 111 222',
                'partner2_name': 'Sarah Wilson',
                'partner2_email': 'sarah@test.com',
                'partner2_phone': '0400 333 444',
                'ceremony_date': date.today() + timedelta(days=60),
                'ceremony_location': 'Royal Botanic Gardens',
                'status': 'Inquiry',
                'fee': 1500.0,
                'travel_fee': 75.0
            },
            {
                'partner1_name': 'David Brown',
                'partner1_email': 'david@test.com',
                'partner1_phone': '0400 555 666',
                'partner2_name': 'Emma Davis',
                'partner2_email': 'emma@test.com',
                'partner2_phone': '0400 777 888',
                'ceremony_date': date.today() - timedelta(days=5),  # Past date for overdue testing
                'ceremony_location': 'St Kilda Beach',
                'status': 'Confirmed',
                'fee': 1800.0,
                'travel_fee': 100.0
            }
        ]
        
        couples_created = 0
        for couple_data in test_couples:
            existing = Couple.query.filter_by(
                partner1_name=couple_data['partner1_name'],
                partner2_name=couple_data['partner2_name'],
                organization_id=org.id
            ).first()
            
            if not existing:
                couple = Couple(
                    organization_id=org.id,
                    celebrant_id=admin.id,
                    **couple_data
                )
                db.session.add(couple)
                couples_created += 1
        
        db.session.commit()
        print(f"✅ {couples_created} test couples created")
        
        # Create test invoices
        couples = Couple.query.filter_by(organization_id=org.id).all()
        invoices_created = 0
        
        # Get existing invoice count to avoid conflicts
        existing_invoice_count = Invoice.query.filter_by(organization_id=org.id).count()
        
        for i, couple in enumerate(couples):
            # Create invoice for each couple
            invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{existing_invoice_count + i + 1:04d}"
            invoice = Invoice(
                organization_id=org.id,
                couple_id=couple.id,
                invoice_number=invoice_number,
                amount=couple.fee or 1000.0,
                currency='AUD',
                description=f'Wedding ceremony services for {couple.partner1_name} & {couple.partner2_name}',
                due_date=date.today() + timedelta(days=14),
                status='pending'
            )
            db.session.add(invoice)
            invoices_created += 1
            
            # Create an overdue invoice for testing
            if i == 0:
                overdue_invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{existing_invoice_count + i + 1:04d}-OVERDUE"
                overdue_invoice = Invoice(
                    organization_id=org.id,
                    couple_id=couple.id,
                    invoice_number=overdue_invoice_number,
                    amount=500.0,
                    currency='AUD',
                    description=f'Deposit payment for {couple.partner1_name} & {couple.partner2_name}',
                    due_date=date.today() - timedelta(days=7),
                    status='pending'
                )
                db.session.add(overdue_invoice)
                invoices_created += 1
        
        db.session.commit()
        print(f"✅ {invoices_created} test invoices created")
        
        print("\n🎉 Database setup complete!")
        print(f"📊 Organization: {org.name}")
        print(f"👤 Admin user: admin@test.com / admin123")
        print(f"💑 Test couples: {len(couples)}")
        print(f"💰 Test invoices: {invoices_created}")
        print(f"🌐 Access the app at: http://localhost:5000")

if __name__ == '__main__':
    setup_database() 