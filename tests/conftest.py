"""
Test configuration and fixtures for the Celebrant Portal
"""
import os
import sys
import tempfile
import pytest
from datetime import datetime, date
from flask import Flask

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app import app as flask_app, db
    from app import User, Couple, CeremonyTemplate, ImportedName
except ImportError:
    # Fallback for when models are in separate file
    from models import db, User, Couple, CeremonyTemplate, ImportedName
    flask_app = Flask(__name__)


@pytest.fixture(scope='session')
def app():
    """Create application for the tests."""
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp()
    
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key'
    })
    
    # Create the database and tables
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.drop_all()
    
    # Clean up the temporary database file
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test runner for the Flask application's Click commands."""
    return app.test_cli_runner()


@pytest.fixture
def db_session(app):
    """Create a database session for testing."""
    with app.app_context():
        db.session.begin()
        yield db.session
        db.session.rollback()


@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            name='Test User',
            is_admin=False
        )
        user.set_password('testpassword')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def admin_user(app):
    """Create an admin test user."""
    with app.app_context():
        user = User(
            username='admin',
            email='admin@example.com',
            name='Admin User',
            is_admin=True
        )
        user.set_password('adminpassword')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def test_couple(app, test_user):
    """Create a test couple."""
    with app.app_context():
        couple = Couple(
            partner1_name='John Doe',
            partner1_email='john@example.com',
            partner1_phone='123-456-7890',
            partner2_name='Jane Smith',
            partner2_email='jane@example.com',
            partner2_phone='098-765-4321',
            ceremony_date=date(2024, 6, 15),
            ceremony_time='2:00 PM',
            ceremony_location='Test Venue',
            ceremony_type='Civil',
            guest_count=50,
            package='Standard',
            fee=500.0,
            status='Confirmed',
            celebrant_id=test_user.id
        )
        db.session.add(couple)
        db.session.commit()
        return couple


@pytest.fixture
def test_template(app, test_user):
    """Create a test ceremony template."""
    with app.app_context():
        template = CeremonyTemplate(
            name='Test Template',
            description='A test ceremony template',
            content='Test ceremony content with {{ partner1_name }} and {{ partner2_name }}',
            ceremony_type='Civil',
            is_default=True,
            celebrant_id=test_user.id
        )
        db.session.add(template)
        db.session.commit()
        return template


@pytest.fixture
def authenticated_client(client, test_user):
    """Create an authenticated test client."""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(test_user.id)
        sess['_fresh'] = True
    return client


@pytest.fixture
def admin_client(client, admin_user):
    """Create an authenticated admin test client."""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(admin_user.id)
        sess['_fresh'] = True
    return client 