import subprocess
import sys
from app.database import create_tables
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_migrations():
    try:
        # Create initial tables if they don't exist
        create_tables()
        logger.info("Database tables created/verified successfully")
        
        # Initialize alembic if not already initialized
        try:
            subprocess.run(["alembic", "current"], check=True)
        except subprocess.CalledProcessError:
            subprocess.run(["alembic", "init", "alembic"], check=True)
            logger.info("Alembic initialized")
        
        # Create a new migration
        subprocess.run(["alembic", "revision", "--autogenerate", "-m", "Initial migration"], check=True)
        logger.info("Migration script created")
        
        # Apply the migration
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        logger.info("Migration applied successfully")
        
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    logger.info(f"Starting database migration for URL: {settings.database_url}")
    run_migrations() 