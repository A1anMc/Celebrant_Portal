#!/bin/bash

# Render Deployment Script for Melbourne Celebrant Portal
# This script ensures proper directory navigation and dependency installation

set -e  # Exit on any error

echo "🚀 Starting Render Deployment..."
echo "Current directory: $(pwd)"
echo "Directory contents: $(ls -la)"

# Check if we're in the right directory structure
if [ -f "requirements.txt" ]; then
    echo "✅ Found requirements.txt in current directory"
    BACKEND_DIR="."
elif [ -f "celebrant-portal-v2/backend/requirements.txt" ]; then
    echo "✅ Found requirements.txt in celebrant-portal-v2/backend/"
    BACKEND_DIR="celebrant-portal-v2/backend"
elif [ -f "backend/requirements.txt" ]; then
    echo "✅ Found requirements.txt in backend/"
    BACKEND_DIR="backend"
else
    echo "❌ Could not find requirements.txt file"
    echo "Available files:"
    find . -name "requirements.txt" -type f
    exit 1
fi

echo "📁 Using backend directory: $BACKEND_DIR"
cd "$BACKEND_DIR"

echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🧪 Testing imports..."
python test_imports.py

echo "✅ Deployment preparation complete!"
echo "Starting application..."

# Start the application
exec gunicorn app.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT 