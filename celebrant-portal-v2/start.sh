#!/bin/bash

# Melbourne Celebrant Portal - Unified Startup Script
# Starts both Next.js frontend and FastAPI backend

echo "🚀 Starting Melbourne Celebrant Portal..."

# Start Next.js frontend in background on port 3000
echo "📱 Starting Next.js frontend on port 3000..."
cd /app/frontend
npm start &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 5

# Start FastAPI backend on port 8000 (main port)
echo "🔧 Starting FastAPI backend on port 8000..."
cd /app

# Run database migrations
echo "🗄️ Running database migrations..."
alembic upgrade head

# Start the FastAPI server
echo "🌟 Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Function to handle shutdown
cleanup() {
    echo "🛑 Shutting down services..."
    kill $FRONTEND_PID 2>/dev/null
    kill $BACKEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Wait for both processes
wait $BACKEND_PID 