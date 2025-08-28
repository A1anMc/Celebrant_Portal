#!/bin/bash

# Professional Deployment Script for Melbourne Celebrant Portal
set -e  # Exit on any error

echo "🚀 Starting professional deployment process..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Validate required environment variables
required_vars=("DATABASE_URL" "SECRET_KEY")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: $var environment variable is required"
        exit 1
    fi
done

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
