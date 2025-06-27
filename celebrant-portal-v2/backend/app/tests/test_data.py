from sqlalchemy.orm import Session
from app.database import SessionLocal, create_tables
from app.models import User, Couple, Ceremony, LegalForm
from app.auth.utils import get_password_hash
from datetime import datetime, timedelta, date, time

def create_test_data():
    db = SessionLocal()
    try:
        # Create test user
        test_user = User(
            email="test@example.com",
            password_hash=get_password_hash("test123"),
            name="Test Celebrant",
            is_active=True,
            is_verified=True,
            business_name="Melbourne Celebrant Services",
            phone="0400123123",
            abn="12345678901"
        )
        db.add(test_user)
        db.flush()

        # Create test couples
        couples_data = [
            {
                "partner_1_first_name": "John",
                "partner_1_last_name": "Doe",
                "partner_1_email": "john@example.com",
                "partner_1_phone": "0400123456",
                "partner_1_date_of_birth": date(1990, 1, 1),
                "partner_2_first_name": "Jane",
                "partner_2_last_name": "Smith",
                "partner_2_email": "jane@example.com",
                "partner_2_phone": "0400123457",
                "partner_2_date_of_birth": date(1991, 2, 2),
                "status": "inquiry",
                "notes": "Initial consultation scheduled",
                "user_id": test_user.id,
                "referral_source": "Google",
                "marketing_consent": "yes"
            },
            {
                "partner_1_first_name": "Michael",
                "partner_1_last_name": "Johnson",
                "partner_1_email": "michael@example.com",
                "partner_1_phone": "0400123458",
                "partner_1_date_of_birth": date(1988, 3, 3),
                "partner_2_first_name": "Sarah",
                "partner_2_last_name": "Williams",
                "partner_2_email": "sarah@example.com",
                "partner_2_phone": "0400123459",
                "partner_2_date_of_birth": date(1989, 4, 4),
                "status": "confirmed",
                "notes": "Deposit paid",
                "user_id": test_user.id,
                "referral_source": "Friend",
                "marketing_consent": "yes"
            }
        ]

        for couple_data in couples_data:
            couple = Couple(**couple_data)
            db.add(couple)
            db.flush()

            # Create ceremony for each couple
            ceremony_date = date.today() + timedelta(days=60)
            ceremony = Ceremony(
                couple_id=couple.id,
                ceremony_date=ceremony_date,
                ceremony_time=time(14, 0),  # 2:00 PM
                estimated_duration=30,
                venue_name="Melbourne Botanical Gardens" if couple.partner_1_first_name == "John" else "Brighton Beach",
                venue_address="Birdwood Avenue, Melbourne" if couple.partner_1_first_name == "John" else "Esplanade, Brighton",
                ceremony_type="civil",
                style="garden" if couple.partner_1_first_name == "John" else "beach",
                guest_count=100,
                vows_type="mixed",
                ring_exchange=True,
                ceremony_fee=800.00,
                travel_fee=50.00,
                status="planned",
                ceremony_notes="Standard ceremony package",
                user_id=test_user.id
            )
            db.add(ceremony)
            db.flush()

            # Create legal form for each couple
            noim_deadline = ceremony_date - timedelta(days=31)  # NOIM must be lodged at least 1 month before
            legal_form = LegalForm(
                couple_id=couple.id,
                ceremony_id=ceremony.id,
                form_type="NOIM",
                form_number=f"NOIM-{couple.id}",
                status="required",
                required_date=date.today(),
                deadline_date=noim_deadline,
                notes="Notice of Intended Marriage form required",
                internal_notes="Follow up with couple for document submission",
                user_id=test_user.id
            )
            db.add(legal_form)

        db.commit()
        print("Test data created successfully!")

    except Exception as e:
        print(f"Error creating test data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_data() 