#!/usr/bin/env python3
"""
Database initialization script for Melbourne Celebrant Portal.
This script can be run separately to initialize the database.
"""

import sys
import os
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.core.database import create_tables, engine
from app.core.config import settings

def main():
    """Initialize the database."""
    print("Initializing Melbourne Celebrant Portal Database...")
    print(f"Database URL: {settings.database_url}")
    
    try:
        # Test database connection
        with engine.connect() as conn:
            print("✓ Database connection successful")
        
        # Create tables
        create_tables()
        print("✓ Database tables created successfully")
        
        print("\nDatabase initialization completed successfully!")
        
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check if the database server is running")
        print("2. Verify the DATABASE_URL environment variable")
        print("3. Ensure database credentials are correct")
        print("4. Check network connectivity to the database server")
        sys.exit(1)

if __name__ == "__main__":
    main()
