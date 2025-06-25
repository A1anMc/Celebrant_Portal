#!/usr/bin/env python3
"""
Backend Setup Script for Melbourne Celebrant Portal
Sets up the FastAPI backend with sample data for development.
"""

import os
import sys
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import SessionLocal, create_tables
from app.models.user import User
from app.models.couple import Couple
from app.models.ceremony import Ceremony
from app.models.invoice import Invoice, InvoiceItem
from app.models.legal_form import LegalForm
from app.models.template import CeremonyTemplate
from app.auth.utils import get_password_hash

def setup_backend():
    """Main setup function."""
    print("🚀 Setting up Melbourne Celebrant Portal Backend...")
    
    try:
        # Create database tables
        print("📋 Creating database tables...")
        create_tables()
        
        # Create session
        db = SessionLocal()
        
        # Create admin user
        create_admin_user(db)
        
        # Create sample data
        create_sample_couples(db)
        create_sample_templates(db)
        create_sample_legal_forms(db)
        create_sample_ceremonies_and_invoices(db)
        
        db.commit()
        print("✅ Backend setup completed successfully!")
        
        # Print summary
        print_setup_summary(db)
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        if 'db' in locals():
            db.rollback()
        return False
    
    finally:
        if 'db' in locals():
            db.close()


def create_admin_user(db: Session):
    """Create the admin user."""
    print("👤 Creating admin user...")
    
    # Check if admin user already exists
    existing_user = db.query(User).filter(User.email == "admin@celebrant.com").first()
    if existing_user:
        print("   Admin user already exists, skipping...")
        return existing_user
    
    # Create admin user
    admin_user = User(
        email="admin@celebrant.com",
        password_hash=get_password_hash("admin123"),
        name="Melbourne Celebrant",
        role="celebrant",
        is_active=True,
        is_verified=True,
        business_name="Melbourne Celebrant Services",
        phone="+61 400 123 456",
        abn="12 345 678 901",
        address="123 Collins Street, Melbourne VIC 3000",
        timezone="Australia/Melbourne",
        currency="AUD"
    )
    
    db.add(admin_user)
    db.flush()
    print("   ✓ Created admin user: admin@celebrant.com")
    
    return admin_user


def create_sample_couples(db: Session):
    """Create sample couples for development."""
    print("💑 Creating sample couples...")
    
    admin_user = db.query(User).filter(User.email == "admin@celebrant.com").first()
    
    sample_couples = [
        {
            "partner_1_first_name": "Emma",
            "partner_1_last_name": "Wilson",
            "partner_1_email": "emma.wilson@email.com",
            "partner_1_phone": "+61 400 111 222",
            "partner_2_first_name": "James",
            "partner_2_last_name": "Thompson",
            "partner_2_email": "james.thompson@email.com",
            "partner_2_phone": "+61 400 333 444",
            "status": "confirmed",
            "notes": "Beautiful garden ceremony planned. Couple is very excited!",
            "referral_source": "Google Search"
        },
        {
            "partner_1_first_name": "Sarah",
            "partner_1_last_name": "Chen",
            "partner_1_email": "sarah.chen@email.com",
            "partner_1_phone": "+61 400 555 666",
            "partner_2_first_name": "Michael",
            "partner_2_last_name": "Roberts",
            "partner_2_email": "michael.roberts@email.com",
            "partner_2_phone": "+61 400 777 888",
            "status": "booked",
            "notes": "Beach ceremony with 80 guests. Requires sound system.",
            "referral_source": "Friend Recommendation"
        },
        {
            "partner_1_first_name": "Lisa",
            "partner_1_last_name": "Martinez",
            "partner_1_email": "lisa.martinez@email.com",
            "partner_1_phone": "+61 400 999 000",
            "partner_2_first_name": "David",
            "partner_2_last_name": "Kim",
            "partner_2_email": "david.kim@email.com",
            "partner_2_phone": "+61 400 111 333",
            "status": "inquiry",
            "notes": "Initial inquiry for winter 2025 ceremony.",
            "referral_source": "Instagram"
        }
    ]
    
    for couple_data in sample_couples:
        couple = Couple(
            **couple_data,
            user_id=admin_user.id,
            primary_contact="partner_1",
            preferred_contact_method="email",
            marketing_consent="yes"
        )
        db.add(couple)
        print(f"   ✓ Created couple: {couple_data['partner_1_first_name']} & {couple_data['partner_2_first_name']}")
    
    db.flush()


def create_sample_templates(db: Session):
    """Create sample ceremony templates."""
    print("📝 Creating ceremony templates...")
    
    admin_user = db.query(User).filter(User.email == "admin@celebrant.com").first()
    
    templates = [
        {
            "name": "Traditional Civil Ceremony",
            "description": "A classic civil ceremony template suitable for most couples",
            "category": "traditional",
            "content": """Welcome family and friends. We are gathered here today to witness and celebrate the marriage of [Partner 1] and [Partner 2].

Marriage is a commitment made in love, kept in love, and renewed by love. Today, [Partner 1] and [Partner 2] choose to publicly declare their love and commitment to each other.

VOWS SECTION:
Do you, [Partner 1], take [Partner 2] to be your lawful wedded [spouse], to have and to hold, in sickness and in health, for richer or poorer, for better or worse, for as long as you both shall live?

Do you, [Partner 2], take [Partner 1] to be your lawful wedded [spouse], to have and to hold, in sickness and in health, for richer or poorer, for better or worse, for as long as you both shall live?

RING EXCHANGE:
The rings you exchange today are symbols of your eternal love and commitment to each other.

PRONOUNCEMENT:
By the power vested in me, I now pronounce you married. You may kiss!""",
            "estimated_duration": 20
        },
        {
            "name": "Modern Beach Ceremony",
            "description": "A relaxed, modern ceremony perfect for beach or outdoor settings",
            "category": "modern",
            "content": """Welcome everyone to this beautiful celebration of love. Today we gather to witness [Partner 1] and [Partner 2] as they begin their journey as a married couple.

Love is patient, love is kind. It is not jealous or boastful, it is not arrogant or rude. Today, [Partner 1] and [Partner 2], you choose to build a life together based on this love.

PERSONAL VOWS:
[Partner 1] and [Partner 2] have chosen to write their own vows to each other.

RING CEREMONY:
These rings represent the unbroken circle of your love. As you wear them, may they remind you of the promises you make today.

PRONOUNCEMENT:
With the power of love and the authority given to me, I pronounce you married. Congratulations!""",
            "estimated_duration": 15
        },
        {
            "name": "Garden Party Ceremony",
            "description": "Perfect for intimate garden celebrations with family and friends",
            "category": "garden",
            "content": """Welcome to this beautiful garden celebration. We are gathered in this lovely setting to witness the marriage of [Partner 1] and [Partner 2].

Like the flowers that bloom in this garden, your love has grown and flourished, bringing beauty and joy to all who know you.

COMMITMENT CEREMONY:
[Partner 1], do you promise to love, support, and cherish [Partner 2] through all seasons of life?

[Partner 2], do you promise to love, support, and cherish [Partner 1] through all seasons of life?

UNITY CEREMONY:
As you plant this tree together, may your love continue to grow and provide shelter and strength for your family.

FINAL BLESSING:
May your marriage be blessed with love, laughter, and happiness. I pronounce you married!""",
            "estimated_duration": 18
        }
    ]
    
    for template_data in templates:
        template = CeremonyTemplate(
            **template_data,
            user_id=admin_user.id,
            is_public=True,
            is_active=True
        )
        db.add(template)
        print(f"   ✓ Created template: {template_data['name']}")
    
    db.flush()


def create_sample_legal_forms(db: Session):
    """Create sample legal forms."""
    print("⚖️ Creating legal forms...")
    
    couples = db.query(Couple).all()
    admin_user = db.query(User).filter(User.email == "admin@celebrant.com").first()
    
    for i, couple in enumerate(couples):
        # Create NOIM form
        deadline = date.today() + timedelta(days=30 + (i * 10))
        
        noim_form = LegalForm(
            form_type="noim",
            status="required" if i == 0 else "submitted" if i == 1 else "approved",
            deadline_date=deadline,
            submitted_date=date.today() - timedelta(days=5) if i > 0 else None,
            approved_date=date.today() - timedelta(days=2) if i == 2 else None,
            couple_id=couple.id,
            user_id=admin_user.id,
            notes=f"NOIM for {couple.full_names} - ceremony planned",
            issuing_authority="Registry of Births, Deaths and Marriages"
        )
        db.add(noim_form)
        print(f"   ✓ Created NOIM for {couple.full_names}")
    
    db.flush()


def create_sample_ceremonies_and_invoices(db: Session):
    """Create sample ceremonies and invoices."""
    print("💒 Creating ceremonies and invoices...")
    
    couples = db.query(Couple).all()
    admin_user = db.query(User).filter(User.email == "admin@celebrant.com").first()
    templates = db.query(CeremonyTemplate).all()
    
    for i, couple in enumerate(couples):
        # Create ceremony (only for first 2 couples)
        if i < 2:
            ceremony_date = date.today() + timedelta(days=60 + (i * 30))
            
            ceremony = Ceremony(
                ceremony_date=ceremony_date,
                ceremony_time="14:00" if i == 0 else "16:30",
                venue_name=f"Beautiful Gardens Venue" if i == 0 else "Seaside Resort",
                venue_address=f"123 Garden Street, Melbourne VIC 3001" if i == 0 else "456 Beach Road, St Kilda VIC 3182",
                ceremony_type="civil",
                guest_count=60 if i == 0 else 80,
                ceremony_fee=900.00 if i == 0 else 1200.00,
                travel_fee=50.00 if i == 0 else 80.00,
                total_fee=950.00 if i == 0 else 1280.00,
                status="confirmed" if i == 0 else "planned",
                couple_id=couple.id,
                template_id=templates[i].id if templates else None,
                user_id=admin_user.id,
                ceremony_notes="Beautiful ceremony planned with personal touches",
                rehearsal_required=True if i == 0 else False,
                rehearsal_date=ceremony_date - timedelta(days=1) if i == 0 else None
            )
            db.add(ceremony)
            db.flush()
            
            # Create invoice
            invoice = Invoice(
                invoice_number=f"INV-2024-{1001 + i}",
                invoice_date=date.today() - timedelta(days=10),
                due_date=ceremony_date - timedelta(days=14),
                subtotal=ceremony.total_fee,
                gst_rate=10.0,
                gst_amount=ceremony.total_fee * 0.10,
                total_amount=ceremony.total_fee * 1.10,
                status="paid" if i == 0 else "sent",
                paid_date=date.today() - timedelta(days=5) if i == 0 else None,
                payment_method="bank_transfer" if i == 0 else None,
                couple_id=couple.id,
                ceremony_id=ceremony.id,
                user_id=admin_user.id,
                notes="Payment for wedding ceremony services"
            )
            db.add(invoice)
            db.flush()
            
            # Create invoice items
            items = [
                {
                    "description": "Wedding Ceremony Service",
                    "quantity": 1,
                    "unit_price": ceremony.ceremony_fee,
                    "total_price": ceremony.ceremony_fee
                },
                {
                    "description": "Travel Fee",
                    "quantity": 1,
                    "unit_price": ceremony.travel_fee,
                    "total_price": ceremony.travel_fee
                }
            ]
            
            for item_data in items:
                item = InvoiceItem(
                    **item_data,
                    invoice_id=invoice.id
                )
                db.add(item)
            
            print(f"   ✓ Created ceremony and invoice for {couple.full_names}")
    
    db.flush()


def print_setup_summary(db: Session):
    """Print setup summary."""
    print("\n📊 Setup Summary:")
    print("=" * 60)
    
    users_count = db.query(User).count()
    couples_count = db.query(Couple).count()
    ceremonies_count = db.query(Ceremony).count()
    invoices_count = db.query(Invoice).count()
    legal_forms_count = db.query(LegalForm).count()
    templates_count = db.query(CeremonyTemplate).count()
    
    print(f"👤 Users: {users_count}")
    print(f"💑 Couples: {couples_count}")
    print(f"💒 Ceremonies: {ceremonies_count}")
    print(f"💰 Invoices: {invoices_count}")
    print(f"⚖️ Legal Forms: {legal_forms_count}")
    print(f"📝 Templates: {templates_count}")
    print("=" * 60)
    
    print("\n🎉 Your FastAPI backend is ready!")
    print("\n🔑 Login Credentials:")
    print("   Email: admin@celebrant.com")
    print("   Password: admin123")
    
    print("\n🚀 Next Steps:")
    print("1. Start the server: uvicorn app.main:app --reload --port 8000")
    print("2. View API docs: http://localhost:8000/docs")
    print("3. Test authentication: POST /api/auth/login")
    print("4. View dashboard: GET /api/dashboard/metrics")
    print("5. Manage couples: GET /api/couples")


if __name__ == "__main__":
    setup_backend() 