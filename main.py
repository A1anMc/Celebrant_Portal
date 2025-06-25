#!/usr/bin/env python3
"""
Root entry point for Melbourne Celebrant Portal.
This file is used when deploying to Render with root directory.
"""

import sys
import os
import logging

# Add the backend directory to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'celebrant-portal-v2', 'backend')
sys.path.insert(0, backend_path)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

try:
    logger.info("Starting Melbourne Celebrant Portal...")
    logger.info(f"Backend path: {backend_path}")
    logger.info(f"Python path: {sys.path[:3]}")  # Show first 3 entries
    
    # Import the FastAPI app
    from app.main import app
    logger.info("✅ Successfully imported FastAPI app")
    
except ImportError as e:
    logger.error(f"❌ Import error: {e}")
    logger.error(f"Current working directory: {os.getcwd()}")
    logger.error(f"Backend path exists: {os.path.exists(backend_path)}")
    if os.path.exists(backend_path):
        logger.error(f"Backend contents: {os.listdir(backend_path)}")
    raise

except Exception as e:
    logger.error(f"❌ Unexpected error during import: {e}")
    raise

# Export the app for uvicorn
__all__ = ['app'] 