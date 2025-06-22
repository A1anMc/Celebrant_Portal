# Celebrant Portal - Enhanced Version

A comprehensive web application for marriage celebrants to manage couples, ceremonies, templates, and email communications with advanced features including batch processing, health monitoring, and backup systems.

## 🚀 New Features & Improvements

### ✨ Enhanced Features
- **Database Indexes**: Added performance indexes for faster queries
- **Comprehensive Error Handling**: Robust error handling with proper logging
- **Health Check System**: Monitor application health and status
- **Backup & Restore**: Complete backup and restore functionality
- **Batch Processing**: Enhanced CSV import with pause/resume capabilities
- **Email Template System**: Four professional email templates included
- **Monitoring Endpoints**: API endpoints for application statistics
- **Enhanced Gmail Integration**: Improved email scanning with fuzzy matching

### 🛠 Technical Improvements
- **Proper Database Migrations**: Flask-Migrate integration with version control
- **Comprehensive Logging**: Application-wide logging with configurable levels
- **Error Templates**: Professional error pages (404, 500, 403)
- **API Documentation**: RESTful API endpoints with proper responses
- **Security Enhancements**: Better session management and error handling
- **Performance Optimization**: Database indexes and query optimization

## 📋 Requirements

- Python 3.8+
- SQLite (default) or PostgreSQL
- Redis (for background tasks)
- Gmail API credentials (for email integration)

## 🔧 Installation & Setup

### 1. Clone and Setup Environment

```bash
git clone <repository-url>
cd celebrant-portal
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file:

```env
# Application Settings
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=sqlite:///celebrant_dev.db

# Admin User (optional - will use defaults if not set)
ADMIN_EMAIL=admin@celebrant.local
ADMIN_PASSWORD=secure_password_here
ADMIN_NAME=Admin User

# Email Configuration (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Redis Configuration (for background tasks)
REDIS_URL=redis://localhost:6379/0
```

### 3. Database Setup

Use the comprehensive setup script:

```bash
python setup_database.py
```

This will:
- Initialize Flask-Migrate
- Create/apply database migrations
- Create admin user
- Set up default templates
- Verify the setup

### 4. Gmail API Setup (Optional but Recommended)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create credentials (OAuth 2.0 Client ID)
5. Download credentials as `credentials.json`
6. Place in the project root directory

### 5. Start the Application

```bash
python app.py
```

The application will be available at `http://localhost:8085`

## 🏥 Health Monitoring

### Health Check Endpoint

```bash
curl http://localhost:8085/api/health
```

### Comprehensive Health Check

```bash
python health_check.py
```

This checks:
- Database connectivity
- Admin user existence
- Gmail credentials
- Data integrity
- File permissions
- Configuration

### JSON Output

```bash
python health_check.py --json
```

## 💾 Backup & Restore

### Create Backup

```bash
# Full backup (database + files)
python backup_restore.py backup

# Database only
python backup_restore.py backup --no-files

# Custom backup directory
python backup_restore.py backup --backup-dir /path/to/backups
```

### List Backups

```bash
python backup_restore.py list
```

### Restore from Backup

```bash
# Full restore
python backup_restore.py restore backup_file.tar.gz

# Database only
python backup_restore.py restore backup_file.tar.gz --no-files

# Files only
python backup_restore.py restore backup_file.tar.gz --no-database
```

### Cleanup Old Backups

```bash
# Keep 10 most recent backups
python backup_restore.py cleanup --keep 10
```

## 📊 API Endpoints

### Health & Monitoring

- `GET /api/health` - Basic health check
- `GET /api/stats` - Application statistics (requires login)

### Data Export

- `GET /api/export/couples` - Export couples data as CSV
- `GET /api/export/email-scan` - Export email scan results
- `GET /api/export/report` - Generate comprehensive report

### Import Management

- `POST /api/import/upload` - Upload CSV for import
- `POST /api/import/map-columns` - Map CSV columns
- `POST /api/import/start` - Start import process
- `POST /api/import/pause` - Pause/resume import
- `POST /api/import/cancel` - Cancel import
- `GET /api/import/status/<id>` - Get import status

## 🗃 Database Schema

### Core Models

- **User**: Celebrant accounts with authentication
- **Couple**: Wedding couples with ceremony details
- **CeremonyTemplate**: Reusable ceremony templates
- **ImportedName**: Names imported from CSV for email scanning
- **ImportSession**: Batch import session tracking

### Indexes Added

Performance indexes on frequently queried fields:
- User email and username
- Couple names, dates, and status
- Template types and names
- Import processing status

## 🔧 Configuration Options

### Application Settings

```python
# config.py
class Config:
    SECRET_KEY = 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///celebrant.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    
    # Background task settings
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
```

## 📝 Email Templates

Four professional email templates included:

1. **confirmation.txt** - Booking confirmations
2. **followup.txt** - Inquiry follow-ups
3. **reminder.txt** - Meeting reminders
4. **final_confirmation.txt** - Final ceremony details

Templates support dynamic placeholders:
- `{partner1_name}`, `{partner2_name}`
- `{ceremony_date}`, `{ceremony_time}`
- `{ceremony_location}`, `{package}`
- `{celebrant_name}`, `{fee}`, `{travel_fee}`

## 🛡 Security Features

- **Password Hashing**: Werkzeug secure password hashing
- **Session Management**: Flask-Login session handling
- **CSRF Protection**: Flask-WTF CSRF tokens
- **Input Validation**: Comprehensive form validation
- **Error Handling**: Secure error messages without information leakage

## 🚨 Error Handling

### Database Errors
- Automatic transaction rollback
- Duplicate entry detection
- Connection failure recovery

### API Errors
- Consistent JSON error responses
- Proper HTTP status codes
- Detailed error logging

### User-Friendly Error Pages
- Custom 404, 500, and 403 pages
- Navigation options for users
- Contact information for support

## 📈 Performance Optimizations

### Database
- Strategic indexes on frequently queried columns
- Efficient relationship mappings
- Query optimization for large datasets

### Application
- Lazy loading of relationships
- Chunked processing for large imports
- Background task processing with Celery

### Caching
- Redis for session storage and task queues
- Static file caching headers
- Database query result caching

## 🔄 Migration Management

### Create New Migration

```bash
flask db migrate -m "Description of changes"
```

### Apply Migrations

```bash
flask db upgrade
```

### Rollback Migration

```bash
flask db downgrade
```

### Migration History

```bash
flask db history
```

## 🧪 Testing

### Health Check Tests

```bash
# Run all health checks
python health_check.py

# Test specific components
python -c "from health_check import check_database_connectivity; print(check_database_connectivity())"
```

### API Testing

```bash
# Test health endpoint
curl http://localhost:8085/api/health

# Test with authentication
curl -X GET http://localhost:8085/api/stats \
  -H "Cookie: session=your-session-cookie"
```

## 📚 Logging

### Log Levels
- **INFO**: General application flow
- **WARNING**: Potential issues
- **ERROR**: Error conditions
- **DEBUG**: Detailed diagnostic information

### Log Files
- `celebrant_portal.log` - Main application log
- Console output for development

### Log Configuration

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('celebrant_portal.log'),
        logging.StreamHandler()
    ]
)
```

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Set production values
2. **Database**: Use PostgreSQL for production
3. **Secret Key**: Generate secure random key
4. **HTTPS**: Enable SSL/TLS
5. **Reverse Proxy**: Use nginx or Apache
6. **Process Manager**: Use Gunicorn or uWSGI

### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8085

CMD ["gunicorn", "--bind", "0.0.0.0:8085", "app:app"]
```

### Environment-Specific Configs

```bash
# Development
export FLASK_ENV=development

# Production
export FLASK_ENV=production
export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex())')
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

### Common Issues

**Database Migration Errors**
```bash
# Reset migrations
rm -rf migrations/
python setup_database.py
```

**Gmail Authentication Issues**
```bash
# Remove existing token and re-authenticate
rm token.pickle
# Visit /scan_emails in browser to re-authenticate
```

**Import Session Stuck**
```bash
# Reset stuck import sessions
python -c "
from app import app, db, ImportSession
from datetime import datetime, timedelta
with app.app_context():
    stuck = ImportSession.query.filter(
        ImportSession.status.in_(['processing', 'paused']),
        ImportSession.updated_at < datetime.utcnow() - timedelta(hours=1)
    ).all()
    for session in stuck:
        session.status = 'failed'
    db.session.commit()
    print(f'Reset {len(stuck)} stuck sessions')
"
```

### Contact

For technical support or questions:
- Check the health check output: `python health_check.py`
- Review logs: `tail -f celebrant_portal.log`
- Create an issue in the repository

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Flask and its ecosystem
- Google APIs for Gmail integration
- Bootstrap for UI components
- SQLAlchemy for database management
- All contributors and users

---

**Version**: 2.0.0  
**Last Updated**: January 2025  
**Compatibility**: Python 3.8+, Flask 2.0+ 