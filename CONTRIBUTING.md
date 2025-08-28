# Contributing to Melbourne Celebrant Portal

Thank you for your interest in contributing to the Melbourne Celebrant Portal! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)
- Git

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/melbourne-celebrant-portal.git
   cd melbourne-celebrant-portal
   ```

2. **Start the development environment**
   ```bash
   ./start-dev.sh
   ```

3. **Verify everything is working**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📋 Development Workflow

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes
- Follow the coding standards outlined below
- Write tests for new functionality
- Update documentation as needed

### 3. Test Your Changes
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### 4. Commit Your Changes
```bash
git add .
git commit -m "feat: add new feature description"
```

### 5. Push and Create a Pull Request
```bash
git push origin feature/your-feature-name
```

## 📝 Coding Standards

### Backend (Python/FastAPI)

#### Code Style
- Use **Black** for code formatting
- Use **isort** for import sorting
- Follow **PEP 8** guidelines
- Use **type hints** for all functions

#### File Structure
```
backend/app/
├── api/v1/          # API endpoints
├── core/            # Configuration and utilities
├── models/          # Database models
├── schemas/         # Pydantic schemas
├── services/        # Business logic
└── tests/           # Test files
```

#### Naming Conventions
- **Files**: snake_case (e.g., `user_service.py`)
- **Classes**: PascalCase (e.g., `UserService`)
- **Functions**: snake_case (e.g., `get_user_by_id`)
- **Variables**: snake_case (e.g., `user_data`)

#### Testing
- Write tests for all new functionality
- Use pytest fixtures for test data
- Aim for 80%+ test coverage
- Test both success and error cases

### Frontend (TypeScript/React)

#### Code Style
- Use **Prettier** for code formatting
- Use **ESLint** for linting
- Follow **TypeScript** strict mode
- Use **functional components** with hooks

#### File Structure
```
frontend/src/
├── app/             # Next.js pages
├── components/      # React components
├── hooks/           # Custom hooks
├── lib/             # Utilities and API client
├── types/           # TypeScript types
└── utils/           # Helper functions
```

#### Naming Conventions
- **Files**: PascalCase for components (e.g., `UserProfile.tsx`)
- **Components**: PascalCase (e.g., `UserProfile`)
- **Functions**: camelCase (e.g., `getUserData`)
- **Variables**: camelCase (e.g., `userData`)

#### Testing
- Write tests for all components
- Use React Testing Library
- Test user interactions and accessibility
- Mock external dependencies

## 🔧 Development Tools

### Pre-commit Hooks
The project uses pre-commit hooks to ensure code quality:

```bash
# Install pre-commit hooks
cd backend
pre-commit install

cd ../frontend
npm run lint
```

### Code Quality Checks
```bash
# Backend
cd backend
black .                    # Format code
isort .                    # Sort imports
flake8 .                   # Lint code
mypy .                     # Type checking
pytest                     # Run tests

# Frontend
cd frontend
npm run lint              # ESLint
npm run type-check        # TypeScript check
npm test                  # Run tests
```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Description**: Clear description of the bug
2. **Steps to reproduce**: Detailed steps to reproduce the issue
3. **Expected behavior**: What you expected to happen
4. **Actual behavior**: What actually happened
5. **Environment**: OS, browser, Node.js version, etc.
6. **Screenshots**: If applicable

## 💡 Feature Requests

When requesting features, please include:

1. **Description**: Clear description of the feature
2. **Use case**: Why this feature is needed
3. **Proposed solution**: How you think it should work
4. **Mockups**: If applicable

## 📚 Documentation

### API Documentation
- API documentation is auto-generated using FastAPI
- Available at http://localhost:8000/docs in development
- Update docstrings for new endpoints

### Code Documentation
- Use docstrings for all functions and classes
- Follow Google docstring format for Python
- Use JSDoc for TypeScript functions

### README Updates
- Update README.md for significant changes
- Add new environment variables to env.example
- Update API endpoint documentation

## 🚀 Deployment

### Testing Before Deployment
```bash
# Run all tests
cd backend && pytest
cd ../frontend && npm test

# Build for production
cd backend && python -m pytest
cd ../frontend && npm run build
```

### Environment Variables
- Never commit sensitive information
- Update `.env.example` files for new variables
- Document all required environment variables

## 🤝 Code Review Process

1. **Pull Request**: Create a detailed PR description
2. **Review**: Address reviewer feedback
3. **Tests**: Ensure all tests pass
4. **Documentation**: Update relevant documentation
5. **Merge**: Once approved, merge to main branch

## 📞 Getting Help

- **Issues**: Create an issue on GitHub
- **Discussions**: Use GitHub Discussions
- **Email**: support@celebrantportal.com

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to the Melbourne Celebrant Portal! 🎉
