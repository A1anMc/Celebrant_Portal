# Development Quick Reference

This guide provides quick reference for common development tasks in the Melbourne Celebrant Portal.

## 🚀 Quick Start Commands

### Start Development Environment
```bash
./start-dev.sh
```

### Stop Development Environment
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

## 🔧 Backend Development

### Start Backend Only
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Tests
```bash
cd backend
pytest                    # Run all tests
pytest -v                # Verbose output
pytest -k "test_auth"    # Run specific test
pytest --cov=app         # With coverage
```

### Code Quality
```bash
cd backend
black .                  # Format code
isort .                  # Sort imports
flake8 .                 # Lint code
mypy .                   # Type checking
```

### Database Operations
```bash
cd backend
# Create tables
python -c "from app.core.database import create_tables; create_tables()"

# Initialize with test data
python init_db.py

# Access database shell
docker-compose exec postgres psql -U postgres -d celebrant_portal
```

## 🎨 Frontend Development

### Start Frontend Only
```bash
cd frontend
npm run dev
```

### Run Tests
```bash
cd frontend
npm test                 # Run all tests
npm run test:watch       # Watch mode
npm run test:coverage    # With coverage
```

### Code Quality
```bash
cd frontend
npm run lint             # ESLint
npm run type-check       # TypeScript check
npm run build            # Production build
```

### Install Dependencies
```bash
cd frontend
npm install              # Install dependencies
npm install package-name # Add new package
```

## 🐳 Docker Commands

### Build Images
```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend
```

### Container Management
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart services
docker-compose restart

# Remove containers and volumes
docker-compose down -v
```

### Access Containers
```bash
# Backend container
docker-compose exec backend bash

# Frontend container
docker-compose exec frontend sh

# Database container
docker-compose exec postgres psql -U postgres
```

## 📊 Database Management

### PostgreSQL Commands
```bash
# Connect to database
docker-compose exec postgres psql -U postgres -d celebrant_portal

# List tables
\dt

# Describe table
\d table_name

# Run SQL query
SELECT * FROM users;

# Exit
\q
```

### Backup and Restore
```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres celebrant_portal > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres -d celebrant_portal < backup.sql
```

## 🔍 Debugging

### Backend Debugging
```bash
# Enable debug mode
export DEBUG=true

# Run with debugger
python -m pdb -m uvicorn app.main:app --reload

# Check logs
docker-compose logs backend
```

### Frontend Debugging
```bash
# Open browser dev tools
# Check console for errors

# Check network requests
# Verify API calls in Network tab

# Debug React components
# Use React Developer Tools extension
```

### Database Debugging
```bash
# Check database connection
docker-compose exec postgres pg_isready -U postgres

# Check database size
docker-compose exec postgres psql -U postgres -c "SELECT pg_size_pretty(pg_database_size('celebrant_portal'));"
```

## 🧪 Testing

### Backend Testing
```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run specific test function
pytest tests/test_auth.py::test_register_user
```

### Frontend Testing
```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- Button.test.tsx

# Run in watch mode
npm run test:watch
```

## 📝 Common Tasks

### Add New API Endpoint
1. Create endpoint in `backend/app/api/v1/`
2. Add schema in `backend/app/schemas/`
3. Add model in `backend/app/models/`
4. Write tests in `backend/tests/`
5. Update API documentation

### Add New Frontend Component
1. Create component in `frontend/src/components/`
2. Add types in `frontend/src/types/`
3. Write tests in `frontend/tests/components/`
4. Update imports where needed

### Add New Environment Variable
1. Add to `backend/.env` or `frontend/.env.local`
2. Update `backend/app/core/config.py` or frontend config
3. Update `docker-compose.yml` if needed
4. Update documentation

### Database Schema Changes
1. Update model in `backend/app/models/`
2. Create migration (when Alembic is set up)
3. Update schemas in `backend/app/schemas/`
4. Update tests
5. Update documentation

## 🚨 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using the port
lsof -i :8000
lsof -i :3000
lsof -i :5432

# Kill process
kill -9 PID
```

#### Docker Issues
```bash
# Clean up Docker
docker system prune -a
docker volume prune

# Rebuild from scratch
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

#### Database Connection Issues
```bash
# Check if database is running
docker-compose ps

# Restart database
docker-compose restart postgres

# Check database logs
docker-compose logs postgres
```

#### Frontend Build Issues
```bash
# Clear Next.js cache
cd frontend
rm -rf .next
npm run build

# Clear node_modules
rm -rf node_modules package-lock.json
npm install
```

#### Backend Import Issues
```bash
# Check Python path
cd backend
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 📚 Useful URLs

### Development
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Database
- **Host**: localhost
- **Port**: 5432
- **Database**: celebrant_portal
- **Username**: postgres
- **Password**: password

## 🔐 Environment Variables

### Backend (.env)
```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/celebrant_portal
SECRET_KEY=your-secret-key-here
DEBUG=true
ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_TELEMETRY_DISABLED=1
```

---

**Note**: This guide is for development only. For production deployment, refer to the main README.md and deployment documentation.
