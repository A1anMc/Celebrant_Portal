# Melbourne Celebrant Portal
## Professional Wedding Management Platform

[![Backend Status](https://img.shields.io/badge/Backend-Live-brightgreen)](https://amelbournecelebrant-6ykh.onrender.com)
[![API Docs](https://img.shields.io/badge/API%20Docs-Available-blue)](https://amelbournecelebrant-6ykh.onrender.com/docs)
[![Version](https://img.shields.io/badge/Version-2.0.0-orange)](https://github.com/A1anMc/amelbournecelebrant)

A comprehensive digital platform designed specifically for professional wedding celebrants to manage couples, ceremonies, legal documentation, and business operations efficiently.

---

## 🚀 **Live Demo**

- **Backend API:** [https://amelbournecelebrant-6ykh.onrender.com](https://amelbournecelebrant-6ykh.onrender.com)
- **API Documentation:** [https://amelbournecelebrant-6ykh.onrender.com/docs](https://amelbournecelebrant-6ykh.onrender.com/docs)
- **Admin Login:** `admin@melbournecelebrant.com` / `admin123`

---

## 📋 **Table of Contents**

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Deployment](#deployment)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

---

## ✨ **Features**

### 🎯 **Core Functionality**
- **Couple Management** - Complete CRM for wedding couples
- **Ceremony Planning** - Timeline and venue management
- **Legal Forms** - Automated NOIM and certificate generation
- **Dashboard Analytics** - Business insights and reporting
- **Document Management** - Secure file storage and sharing
- **Calendar Integration** - Schedule and timeline management

### 🔐 **Security & Privacy**
- **JWT Authentication** - Secure user sessions
- **Role-based Access** - Admin and user permissions
- **Data Encryption** - All sensitive data encrypted
- **GDPR Compliant** - Privacy-first design
- **Audit Logging** - Complete activity tracking

### 📱 **User Experience**
- **Responsive Design** - Works on all devices
- **Modern UI/UX** - Clean, professional interface
- **Real-time Updates** - Live data synchronization
- **Offline Capability** - Works without internet
- **Multi-language** - Internationalization ready

---

## 🛠️ **Tech Stack**

### **Backend**
- **Framework:** FastAPI 0.95.0
- **Database:** PostgreSQL with SQLAlchemy 1.4.53
- **Authentication:** JWT with PyJWT 2.6.0
- **Deployment:** Render.com
- **Documentation:** Swagger/OpenAPI

### **Frontend**
- **Framework:** Next.js 14.2.18
- **Language:** TypeScript
- **Styling:** Tailwind CSS 3.4.0
- **State Management:** React Query
- **Forms:** React Hook Form with Zod validation
- **Deployment:** Vercel (Ready)

### **Development Tools**
- **Version Control:** Git
- **Package Management:** npm/pip
- **Code Quality:** ESLint, Prettier
- **Testing:** Jest, Pytest (Ready)
- **CI/CD:** GitHub Actions (Ready)

---

## 📁 **Project Structure**

```
melbourne-celebrant-portal/
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── api/                     # API Routes
│   │   │   ├── auth.py              # Authentication endpoints
│   │   │   ├── couples.py           # Couple management
│   │   │   ├── dashboard.py         # Dashboard data
│   │   │   └── legal_forms.py       # Legal document generation
│   │   ├── auth/                    # Authentication logic
│   │   ├── models/                  # Database models
│   │   ├── schemas/                 # Pydantic schemas
│   │   ├── database.py              # Database connection
│   │   ├── config.py                # Configuration
│   │   └── main.py                  # FastAPI application
│   ├── requirements.txt             # Python dependencies
│   └── Procfile                     # Deployment configuration
├── frontend/                        # Next.js Frontend
│   ├── src/
│   │   ├── app/                     # Next.js 14 App Router
│   │   ├── components/              # React components
│   │   ├── contexts/                # React contexts
│   │   ├── lib/                     # Utilities
│   │   ├── services/                # API services
│   │   └── types/                   # TypeScript types
│   ├── public/                      # Static assets
│   ├── package.json                 # Node dependencies
│   ├── next.config.js               # Next.js configuration
│   ├── tailwind.config.js           # Tailwind CSS config
│   └── tsconfig.json                # TypeScript config
├── docs/                            # Documentation
│   ├── welcome-guide.md             # User manual
│   ├── marketing-launch-checklist.md # Marketing strategy
│   └── onboarding-email-template.html # Email templates
├── .env.example                     # Environment variables template
├── .gitignore                       # Git ignore rules
├── README.md                        # This file
└── LICENSE                          # MIT License
```

---

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.11+
- Node.js 18+
- PostgreSQL (for production)
- Git

### **1. Clone Repository**
```bash
git clone https://github.com/A1anMc/amelbournecelebrant.git
cd amelbournecelebrant
```

### **2. Backend Setup**
```bash
# Navigate to backend
cd celebrant-portal-v2/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **3. Frontend Setup**
```bash
# Navigate to frontend (in new terminal)
cd frontend

# Install dependencies
npm install

# Set environment variables
cp .env.example .env.local
# Edit .env.local with your API URL

# Run development server
npm run dev
```

### **4. Access Application**
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 🗄️ **Backend Setup**

### **Environment Variables**
Create `.env` file in backend directory:

```env
# Application
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/celebrant_portal
# For development, you can use SQLite:
# DATABASE_URL=sqlite:///./celebrant_portal.db

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

### **Database Setup**

#### **PostgreSQL (Production)**
```bash
# Install PostgreSQL
# macOS
brew install postgresql
brew services start postgresql

# Ubuntu
sudo apt-get install postgresql postgresql-contrib

# Create database
createdb celebrant_portal
```

#### **SQLite (Development)**
```bash
# SQLite database will be created automatically
# No additional setup required
```

### **Run Backend**
```bash
cd celebrant-portal-v2/backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🎨 **Frontend Setup**

### **Environment Variables**
Create `.env.local` file in frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### **Development**
```bash
cd frontend
npm install
npm run dev
```

### **Production Build**
```bash
npm run build
npm start
```

### **Available Scripts**
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript check

---

## 🚀 **Deployment**

### **Backend Deployment (Render.com)**

1. **Create Render Account** and connect GitHub
2. **Create Web Service** with these settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment:** Set all required environment variables

3. **Database Setup:**
   - Create PostgreSQL database on Render
   - Update `DATABASE_URL` environment variable

### **Frontend Deployment (Vercel)**

1. **Connect GitHub** to Vercel
2. **Import Project** and configure:
   - **Framework:** Next.js
   - **Build Command:** `npm run build`
   - **Install Command:** `npm install`

3. **Environment Variables:**
   - Set `NEXT_PUBLIC_API_URL` to your backend URL

### **Alternative Deployment Options**

#### **Docker Deployment**
```bash
# Build and run with Docker
docker build -t celebrant-portal-backend ./backend
docker build -t celebrant-portal-frontend ./frontend

docker run -p 8000:8000 celebrant-portal-backend
docker run -p 3000:3000 celebrant-portal-frontend
```

#### **Traditional VPS Deployment**
- Use nginx as reverse proxy
- Set up SSL certificates with Let's Encrypt
- Configure systemd services for auto-restart

---

## 📚 **API Documentation**

### **Authentication Endpoints**
```http
POST /api/auth/login          # User login
POST /api/auth/register       # User registration
GET  /api/auth/me            # Get current user
PUT  /api/auth/me            # Update user profile
POST /api/auth/change-password # Change password
POST /api/auth/refresh       # Refresh token
POST /api/auth/logout        # User logout
```

### **Couple Management**
```http
GET    /api/couples/         # List couples (with search/pagination)
POST   /api/couples/         # Create new couple
GET    /api/couples/{id}     # Get couple details
PUT    /api/couples/{id}     # Update couple
DELETE /api/couples/{id}     # Delete couple
```

### **Dashboard**
```http
GET /api/dashboard/stats     # Get dashboard statistics
GET /api/dashboard/recent    # Get recent activity
```

### **Legal Forms**
```http
GET    /api/legal-forms/     # List forms
POST   /api/legal-forms/     # Generate new form
GET    /api/legal-forms/{id} # Get form details
PUT    /api/legal-forms/{id} # Update form
DELETE /api/legal-forms/{id} # Delete form
```

### **Interactive API Documentation**
- **Swagger UI:** `/docs`
- **ReDoc:** `/redoc`
- **OpenAPI JSON:** `/openapi.json`

---

## 🧪 **Testing**

### **Backend Tests**
```bash
cd celebrant-portal-v2/backend
pytest tests/ -v
pytest --cov=app tests/  # With coverage
```

### **Frontend Tests**
```bash
cd frontend
npm test
npm run test:coverage
```

### **E2E Tests**
```bash
# Install Playwright
npm install -g @playwright/test
npx playwright install

# Run E2E tests
npm run test:e2e
```

---

## 🔧 **Development**

### **Code Quality**
```bash
# Backend
black app/                    # Format Python code
flake8 app/                   # Lint Python code
mypy app/                     # Type checking

# Frontend
npm run lint                  # ESLint
npm run format               # Prettier
npm run type-check           # TypeScript
```

### **Database Migrations**
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### **Adding New Features**

1. **Backend API Endpoint:**
   - Add route in `app/api/`
   - Create/update models in `app/models/`
   - Add schemas in `app/schemas/`
   - Write tests in `tests/`

2. **Frontend Component:**
   - Create component in `src/components/`
   - Add types in `src/types/`
   - Create service in `src/services/`
   - Add tests in `__tests__/`

---

## 📖 **Documentation**

- **User Guide:** `docs/welcome-guide.md`
- **Marketing Strategy:** `docs/marketing-launch-checklist.md`
- **Email Templates:** `docs/onboarding-email-template.html`
- **API Reference:** Available at `/docs` endpoint
- **Architecture:** `ARCHITECTURE.md`

---

## 🤝 **Contributing**

1. **Fork the repository**
2. **Create feature branch:** `git checkout -b feature/amazing-feature`
3. **Commit changes:** `git commit -m 'Add amazing feature'`
4. **Push to branch:** `git push origin feature/amazing-feature`
5. **Open Pull Request**

### **Development Guidelines**
- Follow existing code style
- Write tests for new features
- Update documentation
- Use conventional commit messages
- Ensure all tests pass

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 **Support**

- **Email:** support@melbournecelebrant.com
- **Phone:** 1300 CELEBRANT (1300 235 327)
- **Documentation:** [help.melbournecelebrant.com](https://help.melbournecelebrant.com)
- **Issues:** [GitHub Issues](https://github.com/A1anMc/amelbournecelebrant/issues)

---

## 🙏 **Acknowledgments**

- Built with ❤️ for the wedding celebrant community
- Inspired by the need for professional digital tools
- Thanks to all beta testers and early adopters

---

## 📊 **Project Status**

- ✅ **Backend:** Production ready and deployed
- ✅ **API:** Fully functional with documentation
- ✅ **Database:** Optimized and secure
- ✅ **Authentication:** JWT-based security
- 🚧 **Frontend:** Ready for deployment
- 🚧 **Testing:** Comprehensive test suite
- 📋 **Documentation:** Complete user guides

**Current Version:** 2.0.0  
**Last Updated:** June 26, 2025  
**Status:** Production Ready

---

*Made with ❤️ in Melbourne, Australia*
