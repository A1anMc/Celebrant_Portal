import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.models import User, Couple

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

@pytest.fixture
def authenticated_client(client, test_user):
    """Create an authenticated test client."""
    from app.core.auth import create_access_token
    
    # Create access token for test user
    access_token = create_access_token(data={"sub": test_user.email})
    
    # Add authorization header to all requests
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    
    return client

@pytest.fixture
def test_user(db_session):
    """Create a test user."""
    from app.core.auth import get_password_hash
    
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test Celebrant"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_couple(db_session, test_user):
    """Create a test couple."""
    from datetime import datetime, timedelta
    
    couple = Couple(
        partner1_name="John Doe",
        partner1_email="john@example.com",
        partner2_name="Jane Smith",
        partner2_email="jane@example.com",
        wedding_date=datetime.now() + timedelta(days=30),  # Future date
        venue="St. Patrick's Cathedral",
        status="Booked",
        celebrant_id=test_user.id
    )
    db_session.add(couple)
    db_session.commit()
    db_session.refresh(couple)
    return couple
