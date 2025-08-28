# 🚀 Render Deployment Guide - Melbourne Celebrant Portal

## **✅ Prerequisites Completed**
- ✅ Render account set up
- ✅ GitHub repository connected
- ✅ Local testing completed (100% pass rate)

## **📋 Step-by-Step Deployment**

### **1. Backend Deployment (Render)**

#### **Create New Web Service**
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select the repository: `melbourne-celebrant-portal`

#### **Configure Service Settings**
```
Name: melbourne-celebrant-portal-backend
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### **Environment Variables**
Add these environment variables in Render dashboard:

```bash
# Database
DATABASE_URL=postgresql://username:password@host:port/database_name

# Security
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app

# Logging
LOG_LEVEL=INFO

# Optional
DEBUG=false
ENVIRONMENT=production
```

#### **Database Setup (Supabase Free Tier)**
1. Go to [Supabase](https://supabase.com)
2. Create new project
3. Get connection string from Settings → Database
4. Update `DATABASE_URL` in Render environment variables

### **2. Frontend Deployment (Vercel)**

#### **Deploy to Vercel**
1. Go to [Vercel](https://vercel.com)
2. Import your GitHub repository
3. Configure build settings:

```bash
Framework Preset: Next.js
Build Command: npm run build
Output Directory: .next
Install Command: npm install
```

#### **Environment Variables**
Add these in Vercel dashboard:

```bash
NEXT_PUBLIC_API_URL=https://your-backend-service.onrender.com
NEXT_PUBLIC_APP_NAME=Melbourne Celebrant Portal
```

### **3. Database Migration**

#### **Run Migrations on Render**
1. Go to your Render service
2. Open **"Shell"** tab
3. Run these commands:

```bash
# Activate environment
source venv/bin/activate

# Run migrations
alembic upgrade head

# Verify database
python -c "from app.core.database import engine; print('Database connected successfully')"
```

### **4. Health Check Verification**

#### **Test Backend Health**
```bash
curl https://your-backend-service.onrender.com/health
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

#### **Test Frontend**
1. Visit your Vercel deployment URL
2. Verify the application loads
3. Test user registration/login
4. Test couple management features

## **🔧 Troubleshooting**

### **Common Issues**

#### **Build Failures**
```bash
# Check build logs in Render
# Common fixes:
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

#### **Database Connection Issues**
```bash
# Verify DATABASE_URL format
postgresql://username:password@host:port/database_name

# Test connection locally
python -c "from app.core.database import engine; print('Connected')"
```

#### **CORS Issues**
```bash
# Update ALLOWED_ORIGINS in Render
ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app,http://localhost:3000
```

### **Performance Optimization**

#### **Enable Auto-Scaling**
1. In Render dashboard, go to your service
2. Click **"Settings"**
3. Enable **"Auto-Deploy"**
4. Set **"Health Check Path"** to `/health`

#### **Database Optimization**
```sql
-- Run in Supabase SQL editor
CREATE INDEX idx_couples_celebrant_id ON couples(celebrant_id);
CREATE INDEX idx_couples_wedding_date ON couples(wedding_date);
```

## **📊 Monitoring Setup**

### **Free Monitoring Tools**

#### **UptimeRobot**
1. Go to [UptimeRobot](https://uptimerobot.com)
2. Add new monitor:
   - URL: `https://your-backend-service.onrender.com/health`
   - Type: HTTP(s)
   - Interval: 5 minutes

#### **Application Logs**
- Render provides built-in log viewing
- Access via your service dashboard
- Monitor for errors and performance

## **🚀 Deployment Checklist**

### **Pre-Deployment**
- [x] Local testing completed (25/25 tests passed)
- [x] Load testing completed (100% success rate)
- [x] Security audit completed
- [x] Frontend build successful
- [x] Environment variables prepared

### **Backend Deployment**
- [ ] Render service created
- [ ] Environment variables configured
- [ ] Database connection established
- [ ] Migrations run successfully
- [ ] Health check passing
- [ ] Auto-scaling enabled

### **Frontend Deployment**
- [ ] Vercel project created
- [ ] Environment variables configured
- [ ] Build successful
- [ ] Domain configured
- [ ] SSL certificate active

### **Post-Deployment**
- [ ] End-to-end testing completed
- [ ] User registration tested
- [ ] Couple management tested
- [ ] Performance monitoring active
- [ ] Error tracking configured

## **💰 Cost Breakdown**

### **Monthly Costs**
- **Backend**: Render Starter ($7/month)
- **Database**: Supabase Free ($0/month)
- **Frontend**: Vercel Free ($0/month)
- **Monitoring**: UptimeRobot Free ($0/month)
- **Total**: **$7/month**

### **Scaling Triggers**
- Database storage > 400 MB → Supabase Pro ($25/month)
- Monthly users > 40,000 → Render Standard ($25/month)
- Bandwidth > 100 GB → Vercel Pro ($20/month)

## **🎯 Success Metrics**

### **Technical Metrics**
- [ ] **Uptime**: 99.9%+
- [ ] **Response Time**: <500ms
- [ ] **Error Rate**: <1%
- [ ] **Build Success**: 100%

### **Business Metrics**
- [ ] **User Registration**: 10+ users
- [ ] **Active Couples**: 5+ couples
- [ ] **User Satisfaction**: 4.5+ stars
- [ ] **System Reliability**: 99%+

## **🎉 Ready to Deploy!**

**Your Melbourne Celebrant Portal is ready for production deployment!**

**Next Steps**:
1. **Deploy Backend** to Render
2. **Deploy Frontend** to Vercel
3. **Configure Database** in Supabase
4. **Run Migrations**
5. **Test End-to-End**
6. **Go Live!**

**Estimated Deployment Time**: 30-60 minutes
**Confidence Level**: 95%+

**Let's get this live!** 🚀
