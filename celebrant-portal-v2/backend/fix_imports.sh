#!/bin/bash

echo "🔧 Ensuring directory structure and init files exist..."

# Create directories if they don't exist
mkdir -p app/utils
mkdir -p app/api
mkdir -p app/auth
mkdir -p app/models
mkdir -p app/schemas
mkdir -p app/services

# Create __init__.py files if they don't exist
touch app/__init__.py
touch app/utils/__init__.py
touch app/api/__init__.py
touch app/auth/__init__.py
touch app/models/__init__.py
touch app/schemas/__init__.py
touch app/services/__init__.py

echo "✅ Directory structure and __init__.py files ensured"

echo "🧪 Running import test..."
PYTHONPATH=. python test_imports.py

if [ $? -eq 0 ]; then
    echo "🎉 All imports working correctly!"
else
    echo "❌ Import test failed. Check the errors above."
    exit 1
fi 