#!/usr/bin/env python3
"""
Data Migration Script: Streamlit SQLite → FastAPI PostgreSQL
Migrates data from the existing celebrant portal to the new system.
"""

import sqlite3
import sys
import os
from datetime import datetime, date
from sqlalchemy.orm import Session
from passlib.context import CryptContext

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import SessionLocal, create_tables
from app.models.user import User
from app.models.couple import Couple
from app.models.ceremony import Ceremony
from app.models.invoice import Invoice, InvoiceItem
from app.models.legal_form import LegalForm
from app.models.template import CeremonyTemplate

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def migrate_data():
    """Main migration function."""
    print("🚀 Starting data migration from Streamlit SQLite to FastAPI PostgreSQL...")
    
    # Path to the existing SQLite database
    sqlite_db_path = "../celebrant_portal.db"
    
    if not os.path.exists(sqlite_db_path):
        print(f"❌ SQLite database not found at {sqlite_db_path}")
        print("Please ensure the Streamlit app database exists.")
        return False
    
    try:
        # Create PostgreSQL tables
        print("📋 Creating PostgreSQL database tables...")
        create_tables()
        
        # Connect to SQLite database
        sqlite_conn = sqlite3.connect(sqlite_db_path)
        sqlite_conn.row_factory = sqlite3.Row  # Enable column access by name
        
        # Connect to PostgreSQL
        pg_session = SessionLocal()
        
        print("🔄 Migrating data...")
        
        # 1. Migrate Users
        migrate_users(sqlite_conn, pg_session)
        
        # 2. Migrate Couples
        migrate_couples(sqlite_conn, pg_session)
        
        # 3. Create sample ceremony templates
        create_sample_templates(pg_session)
        
        # 4. Create sample legal forms for existing couples
        create_sample_legal_forms(pg_session)
        
        # 5. Create sample ceremonies and invoices
        create_sample_ceremonies_and_invoices(pg_session)
        
        pg_session.commit()
        print("✅ Data migration completed successfully!")
        
        # Print summary
        print_migration_summary(pg_session)
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'pg_session' in locals():
            pg_session.rollback()
        return False
    
    finally:
        if 'sqlite_conn' in locals():
            sqlite_conn.close()
        if 'pg_session' in locals():
            pg_session.close()


def migrate_users(sqlite_conn, pg_session):
    """Migrate users from SQLite to PostgreSQL."""
    print("👤 Migrating users...")
    
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    
    for user_row in users:
        # Check if user already exists
        existing_user = pg_session.query(User).filter(User.email == user_row['email']).first()
        if existing_user:
            print(f"   User {user_row['email']} already exists, skipping...")
            continue
        
        # Create new user with enhanced fields
        new_user = User(
            email=user_row['email'],
            password_hash=user_row['password_hash'],  # Keep existing hash
            name=user_row['name'],
            role="celebrant",
            is_active=True,
            is_verified=True,
            business_name="Melbourne Celebrant Services",  # Default business name
            timezone="Australia/Melbourne",
            currency="AUD",
            created_at=datetime.fromisoformat(user_row['created_at']) if user_row['created_at'] else datetime.now()
        )
        
        pg_session.add(new_user)
        print(f"   ✓ Migrated user: {user_row['email']}")
    
    pg_session.commit()


def migrate_couples(sqlite_conn, pg_session):
    """Migrate couples from SQLite to PostgreSQL with enhanced structure."""
    print("💑 Migrating couples...")
    
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM couples")
    couples = cursor.fetchall()
    
    # Get the admin user (should be the only user)
    admin_user = pg_session.query(User).filter(User.email == "admin@celebrant.com").first()
    if not admin_user:
        print("   ❌ Admin user not found, cannot migrate couples")
        return
    
    for couple_row in couples:
        # Parse names (assuming format "First Last")
        partner_1_parts = couple_row['partner_1_name'].split(' ', 1)
        partner_1_first = partner_1_parts[0]
        partner_1_last = partner_1_parts[1] if len(partner_1_parts) > 1 else ""
        
        partner_2_parts = couple_row['partner_2_name'].split(' ', 1)
        partner_2_first = partner_2_parts[0]
        partner_2_last = partner_2_parts[1] if len(partner_2_parts) > 1 else ""
        
        # Create new couple with enhanced structure
        new_couple = Couple(
            # Partner 1
            partner_1_first_name=partner_1_first,
            partner_1_last_name=partner_1_last,
            partner_1_email=couple_row['partner_1_email'],
            
            # Partner 2
            partner_2_first_name=partner_2_first,
            partner_2_last_name=partner_2_last,
            partner_2_email=couple_row['partner_2_email'],
            
            # Contact preferences
            primary_contact="partner_1",
            preferred_contact_method="email",
            
            # Status and notes
            status=couple_row['status'].lower() if couple_row['status'] else "inquiry",
            notes=couple_row['notes'],
            
            # Relationships
            user_id=admin_user.id,
            
            # Timestamps
            created_at=datetime.fromisoformat(couple_row['created_at']) if couple_row['created_at'] else datetime.now()
        )
        
        pg_session.add(new_couple)
        print(f"   ✓ Migrated couple: {partner_1_first} {partner_1_last} & {partner_2_first} {partner_2_last}")
    
    pg_session.commit()


def create_sample_templates(pg_session):
    """Create sample ceremony templates."""
    print("📝 Creating sample ceremony templates...")
    
    templates = [
        {
            "name": "Traditional Civil Ceremony",
            "description": "A classic civil ceremony template suitable for most couples",
            "category": "traditional",
            "content": """Welcome family and friends. We are gathered here today to witness and celebrate the marriage of [Partner 1] and [Partner 2].

Marriage is a commitment made in love, kept in love, and renewed by love. Today, [Partner 1] and [Partner 2] choose to publicly declare their love and commitment to each other.

Do you, [Partner 1], take [Partner 2] to be your lawful wedded [spouse], to have and to hold, in sickness and in health, for richer or poorer, for better or worse, for as long as you both shall live?

Do you, [Partner 2], take [Partner 1] to be your lawful wedded [spouse], to have and to hold, in sickness and in health, for richer or poorer, for better or worse, for as long as you both shall live?

By the power vested in me, I now pronounce you married. You may kiss!""",
            "estimated_duration": 20
        },
        {
            "name": "Modern Beach Ceremony",
            "description": "A relaxed, modern ceremony perfect for beach or outdoor settings",
            "category": "modern",
            "content": """Welcome everyone to this beautiful celebration of love. Today we gather to witness [Partner 1] and [Partner 2] as they begin their journey as a married couple.

Love is patient, love is kind. It is not jealous or boastful, it is not arrogant or rude. Today, [Partner 1] and [Partner 2], you choose to build a life together based on this love.

[Partner 1], do you promise to love, support, and cherish [Partner 2] through all of life's adventures?

[Partner 2], do you promise to love, support, and cherish [Partner 1] through all of life's adventures?

With the power of love and the authority given to me, I pronounce you married. Congratulations!""",
            "estimated_duration": 15
        }
    ]
    
    admin_user = pg_session.query(User).filter(User.email == "admin@celebrant.com").first()
    
    for template_data in templates:
        template = CeremonyTemplate(
            **template_data,
            user_id=admin_user.id if admin_user else None,
            is_public=True,
            is_active=True
        )
        pg_session.add(template)
        print(f"   ✓ Created template: {template_data['name']}")
    
    pg_session.commit()


def create_sample_legal_forms(pg_session):
    """Create sample legal forms for existing couples."""
    print("⚖️ Creating sample legal forms...")
    
    couples = pg_session.query(Couple).all()
    
    for couple in couples:
        # Create NOIM form for each couple
        noim_form = LegalForm(
            form_type="noim",
            status="required",
            deadline_date=date.today().replace(day=28) if date.today().day < 28 else date.today().replace(month=date.today().month+1, day=28),
            couple_id=couple.id,
            user_id=couple.user_id,
            notes="Notice of Intended Marriage - must be submitted at least 1 month before ceremony"
        )
        pg_session.add(noim_form)
        print(f"   ✓ Created NOIM form for {couple.full_names}")
    
    pg_session.commit()


def create_sample_ceremonies_and_invoices(pg_session):
    """Create sample ceremonies and invoices for some couples."""
    print("💒 Creating sample ceremonies and invoices...")
    
    couples = pg_session.query(Couple).limit(3).all()  # Just first 3 couples
    
    for i, couple in enumerate(couples):
        # Create ceremony
        ceremony_date = date.today().replace(month=date.today().month + i + 1)
        
        ceremony = Ceremony(
            ceremony_date=ceremony_date,
            ceremony_time="14:00",
            venue_name=f"Beautiful Gardens Venue {i+1}",
            venue_address=f"123 Garden Street, Melbourne VIC 300{i}",
            ceremony_type="civil",
            guest_count=50 + (i * 20),
            ceremony_fee=800.00,
            travel_fee=50.00,
            total_fee=850.00,
            status="planned",
            couple_id=couple.id,
            user_id=couple.user_id
        )
        pg_session.add(ceremony)
        pg_session.flush()  # Get the ceremony ID
        
        # Create invoice
        invoice = Invoice(
            invoice_number=f"INV-2024-{1000 + i}",
            invoice_date=date.today(),
            due_date=ceremony_date,
            subtotal=850.00,
            gst_amount=85.00,
            total_amount=935.00,
            status="sent",
            couple_id=couple.id,
            ceremony_id=ceremony.id,
            user_id=couple.user_id
        )
        pg_session.add(invoice)
        pg_session.flush()
        
        # Create invoice items
        items = [
            {
                "description": "Wedding Ceremony Service",
                "quantity": 1,
                "unit_price": 800.00,
                "total_price": 800.00
            },
            {
                "description": "Travel Fee",
                "quantity": 1,
                "unit_price": 50.00,
                "total_price": 50.00
            }
        ]
        
        for item_data in items:
            item = InvoiceItem(
                **item_data,
                invoice_id=invoice.id
            )
            pg_session.add(item)
        
        print(f"   ✓ Created ceremony and invoice for {couple.full_names}")
    
    pg_session.commit()


def print_migration_summary(pg_session):
    """Print migration summary statistics."""
    print("\n📊 Migration Summary:")
    print("=" * 50)
    
    users_count = pg_session.query(User).count()
    couples_count = pg_session.query(Couple).count()
    ceremonies_count = pg_session.query(Ceremony).count()
    invoices_count = pg_session.query(Invoice).count()
    legal_forms_count = pg_session.query(LegalForm).count()
    templates_count = pg_session.query(CeremonyTemplate).count()
    
    print(f"👤 Users: {users_count}")
    print(f"💑 Couples: {couples_count}")
    print(f"💒 Ceremonies: {ceremonies_count}")
    print(f"💰 Invoices: {invoices_count}")
    print(f"⚖️ Legal Forms: {legal_forms_count}")
    print(f"📝 Templates: {templates_count}")
    print("=" * 50)
    print("🎉 Your new FastAPI backend is ready!")
    print("\nNext steps:")
    print("1. Start the FastAPI server: uvicorn app.main:app --reload")
    print("2. Visit http://localhost:8000/docs for API documentation")
    print("3. Use the migrated admin credentials: admin@celebrant.com / admin123")


if __name__ == "__main__":
    migrate_data() 