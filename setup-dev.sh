#!/bin/bash

# Melbourne Celebrant Portal - Development Setup Script
# This script sets up a complete development environment with all necessary tools

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check OS
get_os() {
    case "$(uname -s)" in
        Linux*)     echo "linux";;
        Darwin*)    echo "macos";;
        CYGWIN*)    echo "windows";;
        MINGW*)     echo "windows";;
        *)          echo "unknown";;
    esac
}

OS=$(get_os)

print_status "Setting up Melbourne Celebrant Portal Development Environment"
print_status "Operating System: $OS"
echo ""

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# 1. Install Python and pip
print_status "1. Checking Python installation..."
if ! command_exists python3; then
    print_warning "Python 3 is not installed. Please install Python 3.11+ first."
    print_status "Visit: https://www.python.org/downloads/"
    exit 1
else
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python $PYTHON_VERSION is installed"
fi

# 2. Install Node.js and npm
print_status "2. Checking Node.js installation..."
if ! command_exists node; then
    print_warning "Node.js is not installed. Please install Node.js 18+ first."
    print_status "Visit: https://nodejs.org/"
    exit 1
else
    NODE_VERSION=$(node --version)
    NPM_VERSION=$(npm --version)
    print_success "Node.js $NODE_VERSION and npm $NPM_VERSION are installed"
fi

# 3. Install Docker and Docker Compose
print_status "3. Checking Docker installation..."
if ! command_exists docker; then
    print_warning "Docker is not installed. Please install Docker first."
    print_status "Visit: https://docs.docker.com/get-docker/"
    exit 1
else
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
    print_success "Docker $DOCKER_VERSION is installed"
fi

if ! command_exists docker-compose; then
    print_warning "Docker Compose is not installed. Please install Docker Compose first."
    print_status "Visit: https://docs.docker.com/compose/install/"
    exit 1
else
    COMPOSE_VERSION=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
    print_success "Docker Compose $COMPOSE_VERSION is installed"
fi

# 4. Install Git hooks and pre-commit
print_status "4. Setting up Git hooks and pre-commit..."
if ! command_exists pre-commit; then
    print_status "Installing pre-commit..."
    pip3 install pre-commit
    print_success "pre-commit installed"
else
    print_success "pre-commit is already installed"
fi

# Install pre-commit hooks
print_status "Installing pre-commit hooks..."
pre-commit install
pre-commit install --hook-type commit-msg
pre-commit install --hook-type pre-push
print_success "Git hooks installed"

# 5. Setup Python virtual environment
print_status "5. Setting up Python virtual environment..."
if [ ! -d "backend/venv" ]; then
    print_status "Creating Python virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
    print_success "Virtual environment created"
else
    print_success "Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
print_status "Installing Python dependencies..."
cd backend
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
cd ..
print_success "Python dependencies installed"

# 6. Setup Node.js dependencies
print_status "6. Installing Node.js dependencies..."
cd frontend
npm install
cd ..
print_success "Node.js dependencies installed"

# 7. Setup environment files
print_status "7. Setting up environment files..."

# Backend environment
if [ ! -f "backend/.env" ]; then
    print_status "Creating backend/.env..."
    cat > backend/.env << EOF
# Database Configuration
DATABASE_URL=postgresql://postgres:password@localhost:5432/celebrant_portal
TEST_DATABASE_URL=sqlite:///./test.db

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Application Settings
DEBUG=true
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Rate Limiting
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15

# Password Policy
MIN_PASSWORD_LENGTH=8
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_NUMBERS=true
PASSWORD_REQUIRE_SPECIAL=true

# Email (for future use)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EOF
    print_success "backend/.env created"
else
    print_success "backend/.env already exists"
fi

# Frontend environment
if [ ! -f "frontend/.env.local" ]; then
    print_status "Creating frontend/.env.local..."
    cat > frontend/.env.local << EOF
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=Melbourne Celebrant Portal

# Development Settings
NEXT_TELEMETRY_DISABLED=1
NODE_ENV=development

# Feature Flags
NEXT_PUBLIC_ENABLE_ANALYTICS=false
NEXT_PUBLIC_ENABLE_DEBUG=true
EOF
    print_success "frontend/.env.local created"
else
    print_success "frontend/.env.local already exists"
fi

# 8. Setup database
print_status "8. Setting up database..."
if command_exists docker; then
    print_status "Starting PostgreSQL with Docker..."
    docker-compose up -d postgres
    
    # Wait for database to be ready
    print_status "Waiting for database to be ready..."
    sleep 10
    
    # Check if database is ready
    if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
        print_success "Database is ready"
    else
        print_warning "Database might not be ready yet. You may need to wait a bit longer."
    fi
else
    print_warning "Docker not available. Please start PostgreSQL manually."
fi

# 9. Run initial database setup
print_status "9. Running initial database setup..."
cd backend
source venv/bin/activate
python init_db.py
cd ..
print_success "Database initialized"

# 10. Setup development tools
print_status "10. Setting up development tools..."

# Install additional development tools
if command_exists brew; then
    print_status "Installing development tools with Homebrew..."
    brew install jq yq tree htop
elif command_exists apt-get; then
    print_status "Installing development tools with apt..."
    sudo apt-get update
    sudo apt-get install -y jq tree htop
elif command_exists yum; then
    print_status "Installing development tools with yum..."
    sudo yum install -y jq tree htop
fi

# 11. Create development aliases
print_status "11. Setting up development aliases..."

# Create a development script
cat > dev-commands.sh << 'EOF'
#!/bin/bash

# Melbourne Celebrant Portal - Development Commands
# Source this file to get access to development commands

# Function to start development environment
start_dev() {
    echo "🚀 Starting Melbourne Celebrant Portal Development Environment"
    ./start-dev.sh
}

# Function to run backend tests
test_backend() {
    echo "🧪 Running backend tests..."
    cd backend
    source venv/bin/activate
    python -m pytest tests/ -v --cov=app --cov-report=html
    cd ..
}

# Function to run frontend tests
test_frontend() {
    echo "🧪 Running frontend tests..."
    cd frontend
    npm test
    cd ..
}

# Function to run all tests
test_all() {
    echo "🧪 Running all tests..."
    test_backend
    test_frontend
}

# Function to format code
format_code() {
    echo "🎨 Formatting code..."
    cd backend
    source venv/bin/activate
    black app/ tests/
    isort app/ tests/
    cd ..
    
    cd frontend
    npm run format
    cd ..
}

# Function to lint code
lint_code() {
    echo "🔍 Linting code..."
    cd backend
    source venv/bin/activate
    flake8 app/ tests/
    mypy app/
    cd ..
    
    cd frontend
    npm run lint
    cd ..
}

# Function to check code quality
check_quality() {
    echo "✅ Checking code quality..."
    format_code
    lint_code
    test_all
}

# Function to open API documentation
open_api_docs() {
    echo "📚 Opening API documentation..."
    if command -v open >/dev/null 2>&1; then
        open http://localhost:8000/docs
    elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open http://localhost:8000/docs
    else
        echo "Please open http://localhost:8000/docs in your browser"
    fi
}

# Function to open frontend
open_frontend() {
    echo "🌐 Opening frontend..."
    if command -v open >/dev/null 2>&1; then
        open http://localhost:3000
    elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open http://localhost:3000
    else
        echo "Please open http://localhost:3000 in your browser"
    fi
}

# Function to show development status
dev_status() {
    echo "📊 Development Environment Status"
    echo "=================================="
    
    # Check if services are running
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo "✅ Backend API: Running (http://localhost:8000)"
    else
        echo "❌ Backend API: Not running"
    fi
    
    if curl -s http://localhost:3000 >/dev/null 2>&1; then
        echo "✅ Frontend: Running (http://localhost:3000)"
    else
        echo "❌ Frontend: Not running"
    fi
    
    if docker-compose ps postgres | grep -q "Up"; then
        echo "✅ Database: Running"
    else
        echo "❌ Database: Not running"
    fi
}

# Export functions
export -f start_dev test_backend test_frontend test_all format_code lint_code check_quality open_api_docs open_frontend dev_status

echo "🎉 Development commands loaded!"
echo ""
echo "Available commands:"
echo "  start_dev      - Start the development environment"
echo "  test_backend   - Run backend tests"
echo "  test_frontend  - Run frontend tests"
echo "  test_all       - Run all tests"
echo "  format_code    - Format all code"
echo "  lint_code      - Lint all code"
echo "  check_quality  - Run all quality checks"
echo "  open_api_docs  - Open API documentation"
echo "  open_frontend  - Open frontend application"
echo "  dev_status     - Show development environment status"
echo ""
echo "Usage: source dev-commands.sh"
EOF

chmod +x dev-commands.sh
print_success "Development commands script created"

# 12. Create VS Code settings
print_status "12. Setting up VS Code configuration..."
mkdir -p .vscode

cat > .vscode/settings.json << EOF
{
    "python.defaultInterpreterPath": "./backend/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=88"],
    "python.sortImports.args": ["--profile=black", "--line-length=88"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "**/node_modules": true,
        "**/.next": true,
        "**/venv": true
    },
    "typescript.preferences.importModuleSpecifier": "relative",
    "typescript.suggest.autoImports": true,
    "eslint.workingDirectories": ["frontend"],
    "prettier.workingDirectories": ["frontend"]
}
EOF

cat > .vscode/extensions.json << EOF
{
    "recommendations": [
        "ms-python.python",
        "ms-python.black-formatter",
        "ms-python.isort",
        "ms-python.flake8",
        "ms-python.mypy-type-checker",
        "ms-vscode.vscode-typescript-next",
        "esbenp.prettier-vscode",
        "dbaeumer.vscode-eslint",
        "bradlc.vscode-tailwindcss",
        "ms-vscode.vscode-json",
        "yzhang.markdown-all-in-one",
        "ms-vscode.vscode-yaml",
        "ms-azuretools.vscode-docker",
        "github.copilot",
        "github.copilot-chat"
    ]
}
EOF

cat > .vscode/launch.json << EOF
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "program": "\${workspaceFolder}/backend/app/main.py",
            "console": "integratedTerminal",
            "cwd": "\${workspaceFolder}/backend",
            "env": {
                "PYTHONPATH": "\${workspaceFolder}/backend"
            }
        },
        {
            "name": "Python: Current File",
            "type": "python",
            "request": "launch",
            "program": "\${file}",
            "console": "integratedTerminal",
            "cwd": "\${workspaceFolder}/backend"
        }
    ]
}
EOF

print_success "VS Code configuration created"

# 13. Final setup
print_status "13. Final setup..."

# Make scripts executable
chmod +x start-dev.sh
chmod +x setup-dev.sh

# Create a quick start guide
cat > QUICK_START.md << EOF
# 🚀 Quick Start Guide

## Getting Started

1. **Start the development environment:**
   \`\`\`bash
   ./start-dev.sh
   \`\`\`

2. **Load development commands:**
   \`\`\`bash
   source dev-commands.sh
   \`\`\`

3. **Check status:**
   \`\`\`bash
   dev_status
   \`\`\`

## Development Workflow

1. **Start development:**
   \`\`\`bash
   start_dev
   \`\`\`

2. **Run tests:**
   \`\`\`bash
   test_all
   \`\`\`

3. **Format code:**
   \`\`\`bash
   format_code
   \`\`\`

4. **Check quality:**
   \`\`\`bash
   check_quality
   \`\`\`

## URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432

## Useful Commands

- \`start_dev\` - Start development environment
- \`test_backend\` - Run backend tests
- \`test_frontend\` - Run frontend tests
- \`format_code\` - Format all code
- \`lint_code\` - Lint all code
- \`open_api_docs\` - Open API documentation
- \`open_frontend\` - Open frontend application
- \`dev_status\` - Show development status

## VS Code

Open the project in VS Code for the best development experience. The workspace is configured with:

- Python interpreter pointing to the virtual environment
- Code formatting with Black and Prettier
- Linting with Flake8, MyPy, and ESLint
- Import sorting with isort
- Recommended extensions

## Git Workflow

1. Create a feature branch: \`git checkout -b feature/your-feature\`
2. Make your changes
3. Run quality checks: \`check_quality\`
4. Commit your changes: \`git commit -m "feat: your feature description"\`
5. Push your branch: \`git push origin feature/your-feature\`
6. Create a pull request

## Need Help?

- Check the \`DEVELOPER_RULESET.md\` for coding standards
- Review \`CONTRIBUTING.md\` for contribution guidelines
- Read \`README.md\` for project overview
EOF

print_success "Quick start guide created"

# 14. Summary
echo ""
print_success "🎉 Development environment setup complete!"
echo ""
echo "📋 Summary of what was installed:"
echo "  ✅ Python virtual environment with dependencies"
echo "  ✅ Node.js dependencies"
echo "  ✅ Git hooks and pre-commit"
echo "  ✅ Environment configuration files"
echo "  ✅ Database setup"
echo "  ✅ VS Code configuration"
echo "  ✅ Development commands and aliases"
echo ""
echo "🚀 Next steps:"
echo "  1. Start the development environment: ./start-dev.sh"
echo "  2. Load development commands: source dev-commands.sh"
echo "  3. Check status: dev_status"
echo "  4. Open VS Code: code ."
echo ""
echo "📚 Documentation:"
echo "  - README.md - Project overview"
echo "  - DEVELOPER_RULESET.md - Coding standards"
echo "  - CONTRIBUTING.md - Contribution guidelines"
echo "  - QUICK_START.md - Quick start guide"
echo ""
print_success "Happy coding! 🎉"
