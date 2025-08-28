from app.core.database import create_tables, engine, SessionLocal
from app.models import Base, User, Couple
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create a database session
    db = SessionLocal()
    
    try:
        # Create test user
        test_user = User(
            email="test@example.com",
            hashed_password=pwd_context.hash("password123"),
            full_name="Test Celebrant"
        )
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        # Create test couples
        test_couples = [
            Couple(
                partner1_name="John Doe",
                partner1_email="john@example.com",
                partner1_phone="0400123456",
                partner2_name="Jane Smith",
                partner2_email="jane@example.com",
                partner2_phone="0400123457",
                wedding_date=datetime(2024, 12, 25),
                venue="St. Patrick's Cathedral",
                ceremony_type="Wedding",
                status="Booked",
                celebrant_id=test_user.id
            ),
            Couple(
                partner1_name="Robert Brown",
                partner1_email="robert@example.com",
                partner1_phone="0400123458",
                partner2_name="Sarah Wilson",
                partner2_email="sarah@example.com",
                partner2_phone="0400123459",
                wedding_date=datetime(2024, 10, 15),
                venue="Brighton Beach",
                ceremony_type="Wedding",
                status="Inquiry",
                celebrant_id=test_user.id
            )
        ]
        
        for couple in test_couples:
            db.add(couple)
        
        db.commit()
        print("Database initialized successfully with test data!")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database() 