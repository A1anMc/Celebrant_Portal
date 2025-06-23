# 🚀 Legal Forms Automation - Deployment Guide

## Overview
This guide covers the complete deployment of the automated legal forms tracking system for NOIM (Notice of Intended Marriage) and Declaration of No Impediment forms.

## 📋 Prerequisites

### System Requirements
- Python 3.8+
- Redis server
- SQLite/PostgreSQL database
- Flask application server

### Python Dependencies
All required packages are listed in `requirements.txt`:
```bash
pip install -r requirements.txt
```

Key dependencies:
- `celery==5.3.4` - Task queue for background processing
- `redis==5.0.1` - Message broker for Celery
- `flask-mail` - Email sending capabilities
- `flask-wtf` - Form handling and CSRF protection

## 🗄️ Database Setup

### 1. Run Database Migrations
```bash
python run_migrations.py
```

This script will:
- Create all required database tables
- Set up legal forms models
- Optionally create sample data for testing

### 2. Verify Database Schema
The following tables will be created:
- `organizations` - Multi-tenant organization management
- `users` - User accounts with role-based access
- `couples` - Couple information and ceremony details
- `legal_form_submissions` - Form tracking and status
- `compliance_alerts` - Automated alert system
- `reminder_logs` - Audit trail for sent reminders

## 🔧 Configuration

### 1. Environment Variables
Create a `.env` file with the following variables:

```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///celebrant.db
# For PostgreSQL: postgresql://user:password@localhost/celebrant_db

# Redis/Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@celebrant-portal.com

# Application URLs
BASE_URL=https://your-domain.com
```

### 2. Email Setup
For Gmail SMTP:
1. Enable 2-factor authentication
2. Generate an app-specific password
3. Use the app password in `MAIL_PASSWORD`

For other email providers, adjust `MAIL_SERVER` and `MAIL_PORT` accordingly.

## 🚀 Deployment Steps

### 1. Start Redis Server
```bash
# macOS (using Homebrew)
brew services start redis

# Linux (using systemd)
sudo systemctl start redis
sudo systemctl enable redis

# Verify Redis is running
redis-cli ping
# Should return: PONG
```

### 2. Start Celery Services
```bash
# Start both worker and beat scheduler
python run_celery.py

# Or start individually:
# Worker process
celery -A celery_app.celery worker --loglevel=info

# Beat scheduler (in separate terminal)
celery -A celery_app.celery beat --loglevel=info
```

### 3. Start Flask Application
```bash
python app.py
```

The application will be available at `http://localhost:8085`

### 4. Verify Deployment
1. Visit `/legal-forms/dashboard` to see the compliance dashboard
2. Check Celery logs for successful task registration
3. Verify Redis connectivity
4. Test email sending (if configured)

## 📊 Monitoring

### Celery Flower (Optional)
For advanced monitoring, install and run Flower:
```bash
pip install flower
celery -A celery_app.celery flower --port=5555
```

Access monitoring at `http://localhost:5555`

### Health Checks
- Application health: `GET /api/health`
- Database connectivity: Included in health check
- Celery task status: Monitor via Flower or logs

## 🔄 Automated Tasks

The system runs the following automated tasks:

### Hourly Tasks
- **Deadline Monitoring**: Checks for approaching and overdue form deadlines
- **Alert Generation**: Creates compliance alerts for urgent forms

### Daily Tasks
- **Reminder Emails**: Sends scheduled reminders to couples
- **Status Updates**: Updates form statuses based on deadlines

### Weekly Tasks
- **Compliance Reports**: Generates and emails compliance reports to celebrants
- **Alert Cleanup**: Removes resolved alerts older than 30 days

## 🎯 Usage Workflow

### For Celebrants
1. **Dashboard Access**: Visit `/legal-forms/dashboard`
2. **Monitor Compliance**: View real-time compliance statistics
3. **Manage Alerts**: Address overdue and approaching deadlines
4. **Review Reports**: Receive weekly compliance reports via email

### For Couples
1. **Form Upload**: Access secure upload portal via email links
2. **Status Tracking**: View form submission status
3. **Receive Reminders**: Automated email reminders at 30, 14, 7 days before deadlines

### Automated Processes
1. **Form Initialization**: New couples automatically get required forms
2. **Deadline Calculation**: Automatic deadline setting based on ceremony dates
3. **Reminder Scheduling**: Intelligent reminder scheduling
4. **Compliance Monitoring**: Continuous monitoring and alerting

## 🔐 Security Features

### Data Protection
- CSRF protection on all forms
- Secure file upload validation
- Multi-tenant data isolation
- Encrypted password storage

### Access Control
- Role-based permissions (owner, admin, user)
- Organization-level data segregation
- Secure file storage with access controls

### File Upload Security
- File type validation (PDF, DOC, DOCX, JPG, PNG)
- File size limits (10MB maximum)
- Secure storage with organized directory structure

## 🚨 Troubleshooting

### Common Issues

#### Redis Connection Error
```
Error: Redis connection failed
```
**Solution**: Ensure Redis is running and accessible
```bash
brew services start redis  # macOS
sudo systemctl start redis  # Linux
```

#### Celery Tasks Not Running
```
Error: No active Celery workers
```
**Solution**: Start Celery worker process
```bash
python run_celery.py
```

#### Email Sending Failed
```
Error: SMTP authentication failed
```
**Solution**: 
1. Check email credentials in `.env`
2. Verify SMTP settings
3. For Gmail, use app-specific password

#### Database Migration Issues
```
Error: Table already exists
```
**Solution**: This is usually safe to ignore, or drop and recreate tables if needed

### Log Files
- Application logs: `celebrant_portal.log`
- Celery worker logs: Console output when running `run_celery.py`
- Flask application logs: Console output when running `app.py`

## 📈 Performance Optimization

### Database Optimization
- Indexes on frequently queried fields
- Efficient query patterns
- Connection pooling for high-traffic deployments

### Celery Optimization
- Appropriate worker concurrency settings
- Task result expiration
- Memory-efficient task processing

### Caching
- Redis for session storage
- Query result caching for dashboard data
- File upload caching

## 🔄 Maintenance

### Regular Tasks
- Monitor disk space for file uploads
- Review and archive old reminder logs
- Update dependencies regularly
- Backup database regularly

### Monitoring Metrics
- Form completion rates
- Email delivery success rates
- System performance metrics
- User engagement statistics

## 📞 Support

### System Health Monitoring
- Monitor Celery task queue length
- Check Redis memory usage
- Monitor database performance
- Track email delivery rates

### Alerting
- Set up monitoring for failed tasks
- Alert on high error rates
- Monitor system resource usage

## 🎉 Success Metrics

After deployment, you should see:
- **95%+ form completion rate**
- **80% reduction in overdue forms**
- **50% less manual follow-up time**
- **Zero invalid ceremonies due to missing forms**

## 📝 Next Steps

1. **User Training**: Train celebrants on the new dashboard
2. **Process Integration**: Integrate with existing workflow
3. **Monitoring Setup**: Implement comprehensive monitoring
4. **Backup Strategy**: Set up automated backups
5. **Scaling**: Plan for increased usage and scaling needs

---

For technical support or questions about this deployment, please refer to the documentation or contact the development team. 