#!/bin/bash

# Melbourne Celebrant Portal - Development Startup Script
# This script sets up and starts the development environment

set -e

echo "🚀 Starting Melbourne Celebrant Portal Development Environment"
echo "================================================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $port is already in use. Please stop the service using port $port first."
        return 1
    fi
    return 0
}

# Check if required ports are available
echo "🔍 Checking port availability..."
if ! check_port 3000; then
    echo "   Frontend port 3000 is in use"
    read -p "   Do you want to continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

if ! check_port 8000; then
    echo "   Backend port 8000 is in use"
    read -p "   Do you want to continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

if ! check_port 5432; then
    echo "   Database port 5432 is in use"
    read -p "   Do you want to continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create .env files if they don't exist
echo "📝 Setting up environment files..."

if [ ! -f "backend/.env" ]; then
    echo "   Creating backend/.env..."
    cat > backend/.env << EOF
DATABASE_URL=postgresql://postgres:password@localhost:5432/celebrant_portal
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=true
ALLOWED_ORIGINS=http://localhost:3000
ENVIRONMENT=development
EOF
fi

if [ ! -f "frontend/.env.local" ]; then
    echo "   Creating frontend/.env.local..."
    cat > frontend/.env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_TELEMETRY_DISABLED=1
EOF
fi

# Build and start services
echo "🐳 Building and starting Docker services..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "🔍 Checking service status..."

# Check database
if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "✅ Database is ready"
else
    echo "❌ Database is not ready"
fi

# Check backend
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API is ready"
else
    echo "⏳ Backend API is starting..."
    sleep 5
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend API is ready"
    else
        echo "❌ Backend API is not responding"
    fi
fi

# Check frontend
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is ready"
else
    echo "⏳ Frontend is starting..."
    sleep 5
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend is ready"
    else
        echo "❌ Frontend is not responding"
    fi
fi

echo ""
echo "🎉 Development environment is ready!"
echo "================================================================"
echo "📱 Frontend:     http://localhost:3000"
echo "🔧 Backend API:  http://localhost:8000"
echo "📚 API Docs:     http://localhost:8000/docs"
echo "🗄️  Database:     localhost:5432"
echo ""
echo "📋 Useful commands:"
echo "   View logs:     docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart:       docker-compose restart"
echo ""
echo "🔍 To monitor logs in real-time, run:"
echo "   docker-compose logs -f [service_name]"
echo "   (service_name can be: frontend, backend, postgres)"
echo ""
echo "Happy coding! 🚀" 