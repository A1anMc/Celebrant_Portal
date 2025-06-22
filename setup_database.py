#!/usr/bin/env python3
"""
Comprehensive database setup script for the Celebrant Portal.
This script handles database initialization, migrations, and setup.
"""

import os
import sys
import logging
from flask import Flask
from flask_migrate import upgrade, migrate, init, revision
from app import app, db, User, CeremonyTemplate
from werkzeug.security import generate_password_hash

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)

def check_database_exists():
    """Check if the database file exists."""
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    return os.path.exists(db_path)

def initialize_migrations():
    """Initialize Flask-Migrate if not already done."""
    try:
        with app.app_context():
            # Check if migrations directory exists and is initialized
            if not os.path.exists('migrations/versions'):
                logger.info("Initializing Flask-Migrate...")
                init()
                logger.info("Flask-Migrate initialized successfully")
            else:
                logger.info("Flask-Migrate already initialized")
    except Exception as e:
        logger.error(f"Error initializing migrations: {str(e)}")
        return False
    return True

def create_migration_if_needed():
    """Create a new migration if there are model changes."""
    try:
        with app.app_context():
            logger.info("Checking for model changes...")
            migrate(message="Auto-generated migration")
            logger.info("Migration created successfully")
    except Exception as e:
        logger.info(f"No migration needed or error: {str(e)}")

def apply_migrations():
    """Apply all pending migrations."""
    try:
        with app.app_context():
            logger.info("Applying database migrations...")
            upgrade()
            logger.info("Migrations applied successfully")
    except Exception as e:
        logger.error(f"Error applying migrations: {str(e)}")
        return False
    return True

def create_admin_user():
    """Create an admin user if one doesn't exist."""
    try:
        with app.app_context():
            # Check if any admin user exists
            admin = User.query.filter_by(is_admin=True).first()
            if admin:
                logger.info(f"Admin user already exists: {admin.email}")
                return True
            
            # Create new admin user
            admin_email = os.environ.get('ADMIN_EMAIL', 'admin@celebrant.local')
            admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
            admin_name = os.environ.get('ADMIN_NAME', 'Admin User')
            
            admin = User(
                username='admin',
                email=admin_email,
                name=admin_name,
                is_admin=True
            )
            admin.set_password(admin_password)
            
            db.session.add(admin)
            db.session.commit()
            
            logger.info(f"Admin user created successfully!")
            logger.info(f"Email: {admin_email}")
            logger.info(f"Password: {admin_password}")
            logger.warning("IMPORTANT: Please change the admin password after first login!")
            
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        return False
    return True

def create_default_templates():
    """Create default ceremony templates."""
    try:
        with app.app_context():
            # Check if templates already exist
            if CeremonyTemplate.query.count() > 0:
                logger.info("Templates already exist, skipping creation")
                return True
            
            # Get admin user
            admin = User.query.filter_by(is_admin=True).first()
            if not admin:
                logger.warning("No admin user found, skipping template creation")
                return True
            
            # Create default templates
            templates = [
                {
                    'name': 'Simple Civil Ceremony',
                    'description': 'A simple, elegant civil ceremony template',
                    'ceremony_type': 'Civil',
                    'is_default': True,
                    'content': '''Welcome everyone to the marriage ceremony of {partner1_name} and {partner2_name}.

Today, {partner1_name} and {partner2_name} have chosen to unite in marriage, and we are here to witness and celebrate this special moment.

Marriage is a commitment to love, honor, and support each other through all of life's adventures.

{partner1_name}, do you take {partner2_name} to be your spouse, to love and cherish, in sickness and in health, for richer or poorer, for better or worse, for as long as you both shall live?

{partner2_name}, do you take {partner1_name} to be your spouse, to love and cherish, in sickness and in health, for richer or poorer, for better or worse, for as long as you both shall live?

By the power vested in me, I now pronounce you married. You may kiss!'''
                },
                {
                    'name': 'Custom Ceremony Template',
                    'description': 'A customizable ceremony template',
                    'ceremony_type': 'Custom',
                    'is_default': False,
                    'content': '''[Ceremony content to be customized]

Welcome message: [Customize welcome]

Vows: [Custom vows section]

Ring exchange: [Custom ring exchange]

Pronouncement: [Custom pronouncement]

Closing: [Custom closing remarks]'''
                }
            ]
            
            for template_data in templates:
                template = CeremonyTemplate(
                    name=template_data['name'],
                    description=template_data['description'],
                    ceremony_type=template_data['ceremony_type'],
                    is_default=template_data['is_default'],
                    content=template_data['content'],
                    celebrant_id=admin.id
                )
                db.session.add(template)
            
            db.session.commit()
            logger.info(f"Created {len(templates)} default templates")
            
    except Exception as e:
        logger.error(f"Error creating default templates: {str(e)}")
        return False
    return True

def verify_setup():
    """Verify that the setup was successful."""
    try:
        with app.app_context():
            # Check if tables exist
            tables = db.engine.table_names()
            required_tables = ['users', 'couples', 'ceremony_templates', 'imported_names', 'import_sessions']
            
            missing_tables = [table for table in required_tables if table not in tables]
            if missing_tables:
                logger.error(f"Missing tables: {missing_tables}")
                return False
            
            # Check if admin user exists
            admin_count = User.query.filter_by(is_admin=True).count()
            if admin_count == 0:
                logger.error("No admin user found")
                return False
            
            logger.info("Database setup verification successful!")
            logger.info(f"Tables: {len(tables)}")
            logger.info(f"Admin users: {admin_count}")
            logger.info(f"Templates: {CeremonyTemplate.query.count()}")
            
    except Exception as e:
        logger.error(f"Error verifying setup: {str(e)}")
        return False
    return True

def main():
    """Main setup function."""
    logger.info("Starting Celebrant Portal database setup...")
    
    # Step 1: Initialize migrations
    if not initialize_migrations():
        logger.error("Failed to initialize migrations")
        sys.exit(1)
    
    # Step 2: Create migration if needed
    create_migration_if_needed()
    
    # Step 3: Apply migrations
    if not apply_migrations():
        logger.error("Failed to apply migrations")
        sys.exit(1)
    
    # Step 4: Create admin user
    if not create_admin_user():
        logger.error("Failed to create admin user")
        sys.exit(1)
    
    # Step 5: Create default templates
    if not create_default_templates():
        logger.error("Failed to create default templates")
        sys.exit(1)
    
    # Step 6: Verify setup
    if not verify_setup():
        logger.error("Setup verification failed")
        sys.exit(1)
    
    logger.info("Database setup completed successfully!")
    logger.info("You can now start the application with: python app.py")

if __name__ == '__main__':
    main() 