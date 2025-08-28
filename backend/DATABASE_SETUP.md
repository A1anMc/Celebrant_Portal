# Database Setup Guide

## Overview

The Melbourne Celebrant Portal supports both SQLite (for development) and PostgreSQL (for production) databases.

## Quick Start

### Development (SQLite)
For local development, the application will automatically use SQLite if no PostgreSQL connection is configured:

```bash
# The application will automatically use SQLite
python -m uvicorn app.main:app --reload
```

### Production (PostgreSQL)
For production deployment, set the `DATABASE_URL` environment variable:

```bash
export DATABASE_URL="postgresql://username:password@host:port/database_name"
```

## Environment Variables

### Required for Production
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Secret key for JWT tokens
- `ALLOWED_ORIGINS`: Comma-separated list of allowed CORS origins

### Optional
- `INIT_DB`: Set to "true" to initialize database tables on startup
- `DEBUG`: Set to "false" in production
- `LOG_LEVEL`: Logging level (INFO, DEBUG, WARNING, ERROR)

## Database Initialization

### Automatic Initialization
The application will attempt to create database tables on startup. If this fails, the application will continue to run but database operations may fail.

### Manual Initialization
You can manually initialize the database:

```bash
python init_database.py
```

## Troubleshooting

### Connection Issues
If you see errors like "Network is unreachable" or "connection is bad":

1. **Check DATABASE_URL**: Ensure the connection string is correct
2. **Verify Network**: Check if the database server is accessible
3. **Check Credentials**: Verify username, password, and database name
4. **Fallback to SQLite**: The application will automatically fallback to SQLite if PostgreSQL is unavailable

### Health Check
The application provides a health check endpoint:

```bash
curl http://localhost:8000/health
```

This will show the database connection status.

## Deployment

### Render.com
For Render.com deployment:

1. Set environment variables in the Render dashboard
2. Use the provided `render.yaml` configuration
3. The application will automatically handle database initialization

### Docker
For Docker deployment:

```bash
# Build the image
docker build -t celebrant-portal .

# Run with environment variables
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e SECRET_KEY="your-secret-key" \
  celebrant-portal
```

## Database Schema

The application uses SQLAlchemy for database management. Tables are created automatically based on the models defined in `app/models/`.

To view the current schema:
```bash
# For SQLite
sqlite3 celebrant_portal.db ".schema"

# For PostgreSQL
psql $DATABASE_URL -c "\d"
```
