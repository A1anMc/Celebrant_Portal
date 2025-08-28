#!/bin/bash

# Startup script for Melbourne Celebrant Portal

echo "Starting Melbourne Celebrant Portal..."

# Set default port if not provided
export PORT=${PORT:-8000}

# Check if we should initialize the database
if [ "$INIT_DB" = "true" ]; then
    echo "Initializing database..."
    python init_database.py
    if [ $? -ne 0 ]; then
        echo "Warning: Database initialization failed, but continuing..."
    fi
fi

# Start the application
echo "Starting application on port $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
