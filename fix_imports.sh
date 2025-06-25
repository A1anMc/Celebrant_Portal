#!/bin/bash

echo "🔧 Ensuring directory structure and init files exist..."

# Create backend directories if they don't exist
mkdir -p celebrant-portal-v2/backend/app/utils
mkdir -p celebrant-portal-v2/backend/app/api
mkdir -p celebrant-portal-v2/backend/app/auth
mkdir -p celebrant-portal-v2/backend/app/models
mkdir -p celebrant-portal-v2/backend/app/schemas
mkdir -p celebrant-portal-v2/backend/app/services

# Create __init__.py files if they don't exist
touch celebrant-portal-v2/backend/app/__init__.py
touch celebrant-portal-v2/backend/app/utils/__init__.py
touch celebrant-portal-v2/backend/app/api/__init__.py
touch celebrant-portal-v2/backend/app/auth/__init__.py
touch celebrant-portal-v2/backend/app/models/__init__.py
touch celebrant-portal-v2/backend/app/schemas/__init__.py
touch celebrant-portal-v2/backend/app/services/__init__.py

echo "✅ Directory structure and __init__.py files ensured"

echo "🧪 Running import test..."
cd celebrant-portal-v2/backend
PYTHONPATH=. python test_imports.py

if [ $? -eq 0 ]; then
    echo "🎉 All imports working correctly!"
    echo "✅ Python package structure is ready for deployment!"
else
    echo "❌ Import test failed. Check the errors above."
    exit 1
fi 