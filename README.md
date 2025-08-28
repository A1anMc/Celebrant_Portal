# Melbourne Celebrant Portal

A professional web application for wedding celebrants to manage couples, ceremonies, and business operations. Built with modern technologies and designed for deployment on Render and Vercel.

**Latest Update**: Fixed Vercel deployment configuration for monorepo structure.

## 🏗️ Project Structure

```
melbourne-celebrant-portal/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/v1/         # API version 1 endpoints
│   │   ├── core/           # Core configuration and utilities
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic services
│   │   └── main.py         # FastAPI application
│   ├── tests/              # Backend tests
│   ├── alembic/            # Database migrations
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Backend container
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js 14 App Router pages
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── lib/           # Utility functions and API client
│   │   ├── types/         # TypeScript type definitions
│   │   └── utils/         # Helper functions
│   ├── tests/             # Frontend tests
│   ├── package.json       # Node.js dependencies
│   └── Dockerfile         # Frontend container
├── shared/                # Shared types and utilities
├── docker-compose.yml     # Local development setup
└── README.md             # This file
```

## 🌟 Features

- **Professional Dashboard** - Overview of your ceremonies and business metrics
- **Couple Management** - Track wedding couples from inquiry to completion
- **Ceremony Templates** - Manage ceremony scripts and templates (coming soon)
- **Invoice Management** - Handle billing and payments (coming soon)
- **Responsive Design** - Works perfectly on desktop and mobile devices
- **Professional UI** - Gold and black theme with elegant typography

## 🚀 Tech Stack

### Backend
- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL** - Production database (SQLite for development)
- **JWT Authentication** - Secure token-based authentication
- **Pydantic** - Data validation using Python type annotations
- **Alembic** - Database migration system

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icon library
- **Axios** - HTTP client for API calls

## 🛠️ Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd melbourne-celebrant-portal
   ```

2. **Start all services**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Local Development

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp ../frontend/env.example .env
   # Edit .env with your configuration
   ```

5. **Start the development server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env.local
   # Edit .env.local with your configuration
   ```

4. **Start the development server**
   ```bash
   npm run dev
   ```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📊 Database

### Migrations
The project uses Alembic for database migrations:

```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

### Seeding Data
```bash
cd backend
python init_db.py
```

## 🚀 Deployment

### Backend Deployment (Render)

1. **Create a new Web Service on Render**
2. **Connect your GitHub repository**
3. **Configure the service:**
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `backend`

4. **Add environment variables:**
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `SECRET_KEY`: A secure secret key
   - `DEBUG`: `false`
   - `ALLOWED_ORIGINS`: Your frontend domain

### Frontend Deployment (Vercel)

1. **Connect your GitHub repository to Vercel**
2. **Configure the project:**
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

3. **Add environment variables:**
   - `NEXT_PUBLIC_API_URL`: Your backend API URL

## 🔐 Authentication

The application uses JWT (JSON Web Tokens) for authentication:

- Tokens are stored in HTTP-only cookies
- Automatic token refresh
- Protected routes with authentication middleware
- Secure password hashing with bcrypt

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Create new account
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user
- `GET /api/v1/auth/verify` - Verify token

### Couples
- `GET /api/v1/couples` - List all couples
- `POST /api/v1/couples` - Create new couple
- `GET /api/v1/couples/{id}` - Get specific couple
- `PUT /api/v1/couples/{id}` - Update couple
- `DELETE /api/v1/couples/{id}` - Delete couple

## 🎨 Design System

The application uses a professional design system:

### Colors
- **Primary Gold**: `#d4af37` - Main brand color
- **Secondary Dark**: `#1a1a1a` - Text and accents
- **Background**: `#fefdf8` - Warm white background
- **Accent Orange**: `#f17544` - Call-to-action elements

### Typography
- **Headings**: Playfair Display (serif)
- **Body**: Inter (sans-serif)
- Professional hierarchy and spacing

## 📱 Mobile Responsive

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- All modern browsers

## 🔧 Development Tools

### Code Quality
- **Black**: Python code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pre-commit**: Git hooks

### Testing
- **pytest**: Backend testing
- **Jest**: Frontend testing
- **React Testing Library**: Component testing

## 📈 Future Enhancements

- **Ceremony Templates**: Pre-built ceremony scripts
- **Invoice Management**: Billing and payment tracking
- **Calendar Integration**: Sync with Google Calendar
- **Email Notifications**: Automated client communications
- **Document Generation**: PDF ceremony scripts and contracts
- **Payment Processing**: Stripe integration
- **Client Portal**: Couple self-service area
- **Mobile App**: Native iOS/Android applications

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support or questions:
- Create an issue in the GitHub repository
- Email: support@celebrantportal.com

---

**Melbourne Celebrant Portal** - Helping celebrants create beautiful ceremonies with professional tools.
