#!/bin/bash

# Set environment variables for production
export ENVIRONMENT=production
export DEBUG=false

# Start the application
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} 