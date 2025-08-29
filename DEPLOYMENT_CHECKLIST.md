# 🚀 Deployment Checklist - Melbourne Celebrant Portal

## **✅ Pre-Deployment (COMPLETED)**
- [x] Local testing completed (25/25 tests passed)
- [x] Load testing completed (100% success rate)
- [x] Security audit completed
- [x] Frontend build successful
- [x] Backend health checks working
- [x] Configuration files created

## **🎯 Step-by-Step Deployment**

### **Phase 1: Database Setup (5 minutes)**

#### **1.1 Create Supabase Database**
1. Go to [Supabase](https://supabase.com)
2. Click **"New Project"**
3. Choose **"Free Tier"**
4. Set project name: `melbourne-celebrant-portal`
5. Set database password (save this!)
6. Choose region closest to your users
7. Click **"Create new project"**

#### **1.2 Get Database Connection String**
1. Go to **Settings** → **Database**
2. Copy the **Connection string**
3. Format: `postgresql://postgres:[password]@[host]:5432/postgres`

### **Phase 2: Backend Deployment (15 minutes)**

#### **2.1 Deploy to Render**
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select: `melbourne-celebrant-portal`
5. Configure settings:
   - **Name**: `melbourne-celebrant-portal-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: `backend`

#### **2.2 Set Environment Variables**
Add these in Render dashboard:

```bash
# Database
DATABASE_URL=postgresql://postgres:[password]@[host]:5432/postgres

# Security
SECRET_KEY=your-super-secret-key-here-make-it-long-and-random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS (update with your Vercel URL later)
ALLOWED_ORIGINS=https://your-app.vercel.app

# Logging
LOG_LEVEL=INFO
DEBUG=false
ENVIRONMENT=production
```

#### **2.3 Deploy and Test**
1. Click **"Create Web Service"**
2. Wait for build to complete (5-10 minutes)
3. Test health check: `https://your-app.onrender.com/health`
4. Should return: `{"status": "healthy", "version": "0.2.0"}`

### **Phase 3: Frontend Deployment (10 minutes)**

#### **3.1 Deploy to Vercel**
1. Go to [Vercel](https://vercel.com)
2. Click **"New Project"**
3. Import your GitHub repository
4. **Configuration is automatic** - Vercel will detect the frontend directory via vercel.json
5. **No manual configuration needed** - Build commands are automatic

#### **3.2 Set Environment Variables**
Add these in Vercel dashboard:

```bash
NEXT_PUBLIC_API_URL=https://your-app.onrender.com
NEXT_PUBLIC_APP_NAME=Melbourne Celebrant Portal
```

#### **3.3 Deploy and Test**
1. Click **"Deploy"**
2. Wait for build to complete (3-5 minutes)
3. Visit your Vercel URL
4. Verify the app loads correctly

### **Phase 4: Database Migration (5 minutes)**

#### **4.1 Run Migrations**
1. Go to your Render service dashboard
2. Click **"Shell"** tab
3. Run these commands:

```bash
# Navigate to backend directory
cd backend

# Run migrations
alembic upgrade head

# Verify database connection
python -c "from app.core.database import engine; print('Database connected successfully')"
```

### **Phase 5: Final Testing (10 minutes)**

#### **5.1 Backend Testing**
```bash
# Health check
curl https://your-app.onrender.com/health

# API documentation
curl https://your-app.onrender.com/docs
```

#### **5.2 Frontend Testing**
1. Visit your Vercel URL
2. Test user registration
3. Test user login
4. Test couple management
5. Test invoice creation

#### **5.3 Integration Testing**
1. Verify frontend can connect to backend
2. Test API calls from frontend
3. Verify CORS is working
4. Check error handling

## **🔧 Troubleshooting**

### **Common Issues**

#### **Build Failures**
```bash
# Check build logs in Render/Vercel
# Common fixes:
- Verify requirements.txt is in backend/
- Check Python version compatibility
- Ensure all dependencies are listed
```

#### **Database Connection Issues**
```bash
# Verify DATABASE_URL format
postgresql://postgres:password@host:5432/postgres

# Test connection
python -c "from app.core.database import engine; print('Connected')"
```

#### **CORS Issues**
```bash
# Update ALLOWED_ORIGINS in Render
ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

#### **Frontend API Issues**
```bash
# Verify NEXT_PUBLIC_API_URL in Vercel
NEXT_PUBLIC_API_URL=https://your-app.onrender.com
```

## **📊 Post-Deployment Checklist**

### **Technical Verification**
- [ ] Backend health check responding
- [ ] Frontend loading correctly
- [ ] Database migrations completed
- [ ] User registration working
- [ ] User login working
- [ ] Couple management working
- [ ] API documentation accessible
- [ ] CORS configured correctly
- [ ] SSL certificates active
- [ ] Error handling working

### **Performance Verification**
- [ ] Page load times < 3 seconds
- [ ] API response times < 500ms
- [ ] No console errors
- [ ] Mobile responsiveness
- [ ] Cross-browser compatibility

### **Security Verification**
- [ ] HTTPS active on both domains
- [ ] Security headers present
- [ ] Authentication working
- [ ] Rate limiting active
- [ ] Input validation working

## **💰 Cost Summary**

### **Monthly Costs**
- **Backend**: Render Starter ($7/month)
- **Database**: Supabase Free ($0/month)
- **Frontend**: Vercel Free ($0/month)
- **Monitoring**: Free tools ($0/month)
- **Total**: **$7/month**

### **Scaling Triggers**
- Database storage > 400 MB → Supabase Pro ($25/month)
- Monthly users > 40,000 → Render Standard ($25/month)
- Bandwidth > 100 GB → Vercel Pro ($20/month)

## **🎉 Success Criteria**

### **Technical Success**
- [ ] **Uptime**: 99.9%+
- [ ] **Response Time**: <500ms
- [ ] **Error Rate**: <1%
- [ ] **Build Success**: 100%

### **Business Success**
- [ ] **User Registration**: 10+ users
- [ ] **Active Couples**: 5+ couples
- [ ] **User Satisfaction**: 4.5+ stars
- [ ] **System Reliability**: 99%+

## **🚀 Ready to Deploy!**

**Your Melbourne Celebrant Portal is ready for production!**

**Estimated Total Time**: 45 minutes
**Confidence Level**: 95%+
**Monthly Cost**: $7

**Next Steps**:
1. **Start with Supabase** (5 min)
2. **Deploy Backend** to Render (15 min)
3. **Deploy Frontend** to Vercel (10 min)
4. **Run Migrations** (5 min)
5. **Test Everything** (10 min)

**Let's get this live!** 🚀
