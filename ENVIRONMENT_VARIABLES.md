# 🔧 Environment Variables Reference

## **Backend (Render) Environment Variables**

### **Required Variables**
```bash
# Database
DATABASE_URL=postgresql://postgres:your_password@your_host:5432/postgres

# Security
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (update with your Vercel URL)
ALLOWED_ORIGINS=https://your-app.vercel.app

# Logging
LOG_LEVEL=INFO
DEBUG=false
ENVIRONMENT=production
```

### **Optional Variables**
```bash
# Email (if you want email notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# WebSocket (for real-time features)
WEBSOCKET_ENABLED=true
WEBSOCKET_MAX_CONNECTIONS=100

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

## **Frontend (Vercel) Environment Variables**

### **Required Variables**
```bash
# API Configuration
NEXT_PUBLIC_API_URL=https://your-app.onrender.com
NEXT_PUBLIC_APP_NAME=Melbourne Celebrant Portal
```

### **Optional Variables**
```bash
# Analytics
NEXT_PUBLIC_GA_ID=your-google-analytics-id

# Feature Flags
NEXT_PUBLIC_ENABLE_WEBSOCKET=true
NEXT_PUBLIC_ENABLE_ANALYTICS=true
```

## **🔑 Generating Secure Keys**

### **SECRET_KEY Generation**
```bash
# Option 1: Python
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Option 2: Online Generator
# Visit: https://generate-secret.vercel.app/32

# Option 3: Terminal
openssl rand -base64 32
```

### **Example SECRET_KEY**
```
SECRET_KEY=your-generated-secret-key-here-32-characters-long
```

## **🌐 URL Examples**

### **Render Backend URLs**
```
Production: https://melbourne-celebrant-portal-backend.onrender.com
Health Check: https://melbourne-celebrant-portal-backend.onrender.com/health
API Docs: https://melbourne-celebrant-portal-backend.onrender.com/docs
```

### **Vercel Frontend URLs**
```
Production: https://melbourne-celebrant-portal.vercel.app
Preview: https://melbourne-celebrant-portal-git-main.vercel.app
```

### **Supabase Database URLs**
```
Connection String: postgresql://postgres:password@host:5432/postgres
Dashboard: https://supabase.com/dashboard/project/your-project-id
```

## **🔧 Configuration Examples**

### **Complete Backend Configuration**
```bash
# Database
DATABASE_URL=postgresql://postgres:mypassword123@db.abcdefgh.supabase.co:5432/postgres

# Security
SECRET_KEY=my-super-secret-key-32-characters-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=https://melbourne-celebrant-portal.vercel.app

# Logging
LOG_LEVEL=INFO
DEBUG=false
ENVIRONMENT=production
```

### **Complete Frontend Configuration**
```bash
# API
NEXT_PUBLIC_API_URL=https://melbourne-celebrant-portal-backend.onrender.com
NEXT_PUBLIC_APP_NAME=Melbourne Celebrant Portal
```

## **✅ Verification Commands**

### **Test Backend Health**
```bash
curl https://your-app.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-28T11:54:11.303742",
  "version": "0.2.0",
  "message": "Melbourne Celebrant Portal is running"
}
```

### **Test Database Connection**
```bash
# In Render shell
python -c "from app.core.database import engine; print('Database connected successfully')"
```

### **Test Frontend API Connection**
```bash
# In browser console
fetch('https://your-app.onrender.com/health').then(r => r.json()).then(console.log)
```

## **🚨 Security Notes**

### **Never Commit These**
- ✅ `SECRET_KEY`
- ✅ `DATABASE_URL`
- ✅ `SMTP_PASSWORD`
- ✅ Any API keys

### **Safe to Commit**
- ✅ `NEXT_PUBLIC_*` variables (they're public anyway)
- ✅ `LOG_LEVEL`
- ✅ `DEBUG`
- ✅ `ENVIRONMENT`

## **🔧 Troubleshooting**

### **Common Issues**

#### **CORS Errors**
```bash
# Make sure ALLOWED_ORIGINS includes your Vercel URL
ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

#### **Database Connection Errors**
```bash
# Verify DATABASE_URL format
postgresql://username:password@host:port/database_name

# Test connection
python -c "from app.core.database import engine; print('Connected')"
```

#### **Frontend API Errors**
```bash
# Verify NEXT_PUBLIC_API_URL
NEXT_PUBLIC_API_URL=https://your-app.onrender.com

# Check browser console for CORS errors
```

## **📋 Deployment Checklist**

### **Before Deployment**
- [ ] Generate secure `SECRET_KEY`
- [ ] Set up Supabase database
- [ ] Get database connection string
- [ ] Prepare Vercel URL for CORS

### **During Deployment**
- [ ] Set all environment variables in Render
- [ ] Set all environment variables in Vercel
- [ ] Test health checks
- [ ] Verify database connection

### **After Deployment**
- [ ] Test user registration
- [ ] Test user login
- [ ] Test couple management
- [ ] Verify CORS is working
- [ ] Check error handling

## **🎯 Ready to Deploy!**

**All configuration files are ready!**

**Next Steps**:
1. **Copy the environment variables** above
2. **Follow the deployment checklist**
3. **Set variables in Render and Vercel**
4. **Deploy and test!**

**Good luck with the deployment!** 🚀
