# Professional Deployment Guide

## Overview

This guide outlines the professional approach to deploying the Melbourne Celebrant Portal across different environments.

## Environment Strategy

### Development
- **Database**: SQLite (auto-created)
- **Configuration**: Local `.env` file
- **Features**: Debug mode, auto-reload, detailed logging

### Staging
- **Database**: PostgreSQL (test instance)
- **Configuration**: Environment variables
- **Features**: Production-like setup, testing environment

### Production
- **Database**: PostgreSQL (managed service)
- **Configuration**: Secure environment variables
- **Features**: Optimized performance, security hardened

## Deployment Process

### 1. Pre-Deployment Checklist

```bash
# Validate environment
./deploy.sh

# Check database migrations
alembic current
alembic history

# Security audit
python -c "from app.core.config import settings; print('Security check passed')"
```

### 2. Database Migration Strategy

```bash
# Development
python init_database.py

# Staging/Production
alembic upgrade head
alembic stamp head  # Mark as up-to-date
```

### 3. Environment Variables

#### Required for All Environments
```bash
DATABASE_URL=postgresql://user:pass@host:port/db
SECRET_KEY=your-super-secret-key-32-chars-minimum
ENVIRONMENT=production|staging|development
```

#### Production-Specific
```bash
DEBUG=false
LOG_LEVEL=INFO
ALLOWED_ORIGINS=https://yourdomain.com
CSRF_TOKEN_SECRET=your-csrf-secret
```

### 4. Security Best Practices

- ✅ Use managed PostgreSQL service
- ✅ Rotate secrets regularly
- ✅ Enable HTTPS only
- ✅ Implement rate limiting
- ✅ Use secure session cookies
- ✅ Validate all inputs
- ✅ Monitor application logs

### 5. Monitoring and Health Checks

```bash
# Health check endpoint
curl https://your-app.com/health

# Expected response
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "0.2.0"
}
```

## Render.com Deployment

### 1. Environment Variables
Set these in Render dashboard:
- `DATABASE_URL`
- `SECRET_KEY`
- `ENVIRONMENT=production`
- `DEBUG=false`
- `ALLOWED_ORIGINS`

### 2. Build Command
```bash
pip install -r requirements.txt
```

### 3. Start Command
```bash
./deploy.sh && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### 4. Health Check URL
```
https://your-app.onrender.com/health
```

## Database Management

### Creating Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Backup Strategy
```bash
# PostgreSQL backup
pg_dump $DATABASE_URL > backup.sql

# Restore backup
psql $DATABASE_URL < backup.sql
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check DATABASE_URL format
   - Verify network connectivity
   - Check database credentials

2. **Migration Errors**
   - Run `alembic current` to check status
   - Use `alembic stamp head` to sync
   - Check migration history

3. **Application Won't Start**
   - Check environment variables
   - Verify port availability
   - Check application logs

### Log Analysis
```bash
# View application logs
tail -f app.log

# Check database logs
# (Depends on your database service)
```

## Performance Optimization

### Database
- Use connection pooling
- Implement database indexing
- Regular maintenance tasks

### Application
- Enable compression
- Use CDN for static assets
- Implement caching strategies

### Monitoring
- Set up application monitoring
- Database performance monitoring
- Error tracking and alerting

## Security Checklist

- [ ] HTTPS enabled
- [ ] Secure headers configured
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation implemented
- [ ] SQL injection protection
- [ ] XSS protection
- [ ] CSRF protection
- [ ] Secure session management
- [ ] Regular security updates
