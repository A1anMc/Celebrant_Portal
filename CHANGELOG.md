# Changelog

All notable changes to the Melbourne Celebrant Portal will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive project refactoring and restructuring
- Docker-based development environment
- API versioning system (`/api/v1/`)
- Testing infrastructure for both backend and frontend
- Enhanced documentation and setup guides
- Shared TypeScript types
- Health check endpoint

### Changed
- Reorganized project structure for better scalability
- Updated import paths to use new package structure
- Enhanced development dependencies and tools
- Improved error handling and validation

### Fixed
- Import path issues in refactored structure
- Database connection configuration
- Environment variable handling

## [0.1.0] - 2024-01-XX

### Added
- Initial project setup
- FastAPI backend with JWT authentication
- Next.js frontend with TypeScript
- User registration and login functionality
- Couple management system
- Basic dashboard interface
- Professional UI design system
- Responsive design for mobile devices
- PostgreSQL database integration
- SQLAlchemy ORM models
- Pydantic data validation
- CSRF protection
- Rate limiting middleware
- Password hashing with bcrypt
- Auto-generated API documentation

### Technical Features
- FastAPI 0.109.0 backend
- Next.js 14 frontend with App Router
- TypeScript for type safety
- Tailwind CSS for styling
- Lucide React for icons
- Axios for API communication
- SQLite development database
- PostgreSQL production database
- Docker containerization
- Render deployment configuration

### Security
- JWT token-based authentication
- Password policy enforcement
- Account lockout protection
- Failed login attempt tracking
- Secure session management
- CORS configuration
- Trusted host middleware

---

## Version History

### Version 0.1.0 (Initial Release)
- **Date**: January 2024
- **Status**: Development
- **Features**: Core authentication and couple management
- **Architecture**: Monolithic structure with basic separation

### Version 0.2.0 (Refactored Release)
- **Date**: January 2024
- **Status**: Development
- **Features**: Refactored architecture with modern practices
- **Architecture**: Microservices-ready with API versioning

---

## Release Notes

### Breaking Changes
- **v0.2.0**: API endpoints now use `/api/v1/` prefix
- **v0.2.0**: Import paths have changed due to restructuring
- **v0.2.0**: Docker-based development environment

### Migration Guide
When upgrading from v0.1.0 to v0.2.0:

1. **Update API calls**: All endpoints now require `/api/v1/` prefix
2. **Environment setup**: Use Docker Compose for development
3. **Database**: PostgreSQL is now the default database
4. **Dependencies**: Updated to latest versions with new tools

### Deprecation Notices
- SQLite database (development only)
- Old import paths (removed in v0.2.0)
- Non-versioned API endpoints (deprecated in v0.2.0)

---

## Contributing to the Changelog

When adding entries to the changelog, please follow these guidelines:

1. **Use the appropriate section**: Added, Changed, Deprecated, Removed, Fixed, Security
2. **Be descriptive**: Explain what changed and why
3. **Include breaking changes**: Clearly mark any breaking changes
4. **Add migration notes**: Help users upgrade smoothly
5. **Include version numbers**: Use semantic versioning

### Changelog Entry Format
```markdown
### Added
- New feature description

### Changed
- Changed feature description

### Fixed
- Bug fix description

### Security
- Security improvement description
```

---

**Note**: This changelog is maintained by the development team. For detailed technical changes, please refer to the git commit history.
