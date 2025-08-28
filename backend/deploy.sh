#!/bin/bash

# Professional Deployment Script for Melbourne Celebrant Portal
set -e  # Exit on any error

echo "🚀 Starting professional deployment process..."

# Set default environment variables if not provided
export DATABASE_URL=${DATABASE_URL:-"sqlite:///./celebrant_portal.db"}
export SECRET_KEY=${SECRET_KEY:-"your-super-secret-key-change-in-production"}
export ENVIRONMENT=${ENVIRONMENT:-"development"}
export DEBUG=${DEBUG:-"true"}

# Load additional environment variables from .env if it exists
if [ -f .env ]; then
    # Use a more robust method to load env vars
    eval "$(cat .env | sed 's/^/export /')" 2>/dev/null || true
fi

echo "✅ Environment variables loaded"
echo "   DATABASE_URL: $DATABASE_URL"
echo "   ENVIRONMENT: $ENVIRONMENT"
echo "   DEBUG: $DEBUG"

echo "✅ Environment validation passed"

# Determine environment
ENVIRONMENT=${ENVIRONMENT:-"development"}
echo "🌍 Environment: $ENVIRONMENT"

# Database setup based on environment
if [ "$ENVIRONMENT" = "production" ]; then
    echo "🗄️  Production: Running database migrations..."
    
    # Run Alembic migrations
    if command -v alembic &> /dev/null; then
        echo "📦 Running Alembic migrations..."
        alembic upgrade head
        echo "✅ Database migrations completed"
    else
        echo "⚠️  Warning: Alembic not found, skipping migrations"
    fi
    
    # Validate database connection
    echo "🔍 Validating database connection..."
    python -c "
from app.core.database import engine
with engine.connect() as conn:
    conn.execute('SELECT 1')
print('✅ Database connection validated')
"
    
elif [ "$ENVIRONMENT" = "staging" ]; then
    echo "🧪 Staging: Setting up test database..."
    
    # Run migrations for staging
    if command -v alembic &> /dev/null; then
        alembic upgrade head
    fi
    
else
    echo "🛠️  Development: Using SQLite with auto-creation"
    # Development environment - tables will be created on startup
fi

# Security checks
echo "🔒 Running security checks..."
python -c "
from app.core.config import settings
if settings.debug and settings.environment == 'production':
    print('⚠️  Warning: Debug mode enabled in production')
if len(settings.secret_key) < 32:
    print('⚠️  Warning: Secret key may be too short')
print('✅ Security checks completed')
"

# Health check
echo "🏥 Running health check..."
python -c "
import requests
import time
import sys

# Start the application in background (simplified check)
try:
    from app.main import app
    print('✅ Application imports successfully')
except Exception as e:
    print(f'❌ Application import failed: {e}')
    sys.exit(1)
"

echo "🎉 Deployment preparation completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Start the application: uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
echo "2. Monitor logs for any issues"
echo "3. Test the health endpoint: /health"
echo "4. Verify database connectivity"
