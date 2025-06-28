# 🔄 Deployment Migration Guide
## From Dual-Service to Unified Render Deployment

This guide explains the migration from the previous deployment architecture (Render backend + Vercel frontend) to the new unified Render deployment.

---

## 📋 What Changed

### **Previous Architecture**
```
┌─────────────────┐    ┌─────────────────┐
│   Vercel        │    │   Render        │
│   Frontend      │◄───┤   Backend       │
│   (Next.js)     │    │   (FastAPI)     │
│   Port 3000     │    │   Port 8000     │
└─────────────────┘    └─────────────────┘
```

### **New Architecture**
```
┌─────────────────────────────────────┐
│   Render - Unified Container        │
│   ┌─────────────┐ ┌─────────────┐   │
│   │ Next.js     │ │ FastAPI     │   │
│   │ Port 3000   │ │ Port 8000   │   │
│   │ (Internal)  │ │ (Public)    │   │
│   └─────────────┘ └─────────────┘   │
└─────────────────────────────────────┘
```

---

## 🎯 Benefits of Migration

### **Simplified Deployment**
- ❌ **Before**: Two separate services to manage
- ✅ **After**: Single service deployment

### **Reduced Complexity**
- ❌ **Before**: CORS configuration between services
- ✅ **After**: No CORS issues (same host)

### **Cost Optimization**
- ❌ **Before**: Two service limits to manage
- ✅ **After**: Single service, reduced resource usage

### **Easier Management**
- ❌ **Before**: Monitor two services, two sets of logs
- ✅ **After**: One service, unified logging

---

## 🛠️ Migration Steps

### **Step 1: Backup Current Deployment**
If you have an existing deployment:
1. **Export environment variables** from both services
2. **Backup database** (if needed)
3. **Note current URLs** for reference

### **Step 2: Prepare New Deployment**
1. **Update your repository** with new files:
   ```
   celebrant-portal-v2/
   ├── Dockerfile              # New unified build
   ├── start.sh                # Startup script
   ├── render.yaml             # Deployment config
   ├── Procfile                # Process definition
   └── RENDER_DEPLOYMENT.md    # Deployment guide
   ```

2. **Updated files**:
   - `backend/app/main.py` - Added frontend proxy
   - `backend/app/config.py` - Updated CORS handling
   - `backend/requirements.txt` - Added httpx dependency
   - `frontend/next.config.js` - Updated for unified deployment

### **Step 3: Deploy New Architecture**
1. **Create new Render service** using blueprint or manual setup
2. **Link existing database** or create new one
3. **Configure environment variables**:
   ```bash
   ENVIRONMENT=production
   DEBUG=false
   NODE_ENV=production
   SECRET_KEY=<secure-key>
   DATABASE_URL=<database-connection>
   NEXT_PUBLIC_API_URL=""  # Empty for same-host
   CORS_ORIGINS=["*"]      # Unified deployment
   ```

### **Step 4: Test New Deployment**
1. **Verify health check**: `https://your-app.onrender.com/health`
2. **Test frontend**: Application loads correctly
3. **Test API**: Login and dashboard work
4. **Check styling**: Melbourne Celebrant branding displays

### **Step 5: Update DNS (if using custom domain)**
1. **Point domain** to new Render service
2. **Update any external integrations**
3. **Test with custom domain**

### **Step 6: Cleanup Old Services**
1. **Verify new deployment** is working correctly
2. **Delete old Vercel project** (if no longer needed)
3. **Delete old Render backend service** (if separate)
4. **Clean up old environment variables**

---

## 🔧 Technical Changes

### **Backend Changes**

#### **main.py Updates**
```python
# Added imports
from fastapi.staticfiles import StaticFiles
from fastapi.responses import Response
import httpx

# Added middleware for proxying
@app.middleware("http")
async def proxy_frontend(request: Request, call_next):
    # Proxy non-API requests to Next.js frontend
    if not request.url.path.startswith("/api"):
        # Forward to localhost:3000
        ...
```

#### **config.py Updates**
```python
# Updated CORS handling
@property
def cors_origins(self) -> List[str]:
    if self.cors_origins_str == '["*"]':
        return ["*"]  # Allow for unified deployment
    return [origin.strip() for origin in self.cors_origins_str.split(",")]
```

#### **requirements.txt Updates**
```python
# Added for frontend proxying
httpx==0.25.2
```

### **Frontend Changes**

#### **next.config.js Updates**
```javascript
env: {
  // Empty API URL for same-host deployment
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || (
    process.env.NODE_ENV === 'production' 
      ? '' // Same host in production
      : 'http://localhost:8000' // Separate in development
  ),
},

async rewrites() {
  // No rewrites needed in production (unified deployment)
  if (process.env.NODE_ENV === 'production') {
    return [];
  }
  // Only rewrite in development
  ...
}
```

---

## 🚨 Troubleshooting Migration

### **Common Issues**

#### **Build Failures**
```bash
# Issue: Frontend build fails
# Solution: Check Node.js version compatibility in Dockerfile

# Issue: Backend dependencies fail
# Solution: Verify requirements.txt includes httpx
```

#### **Runtime Issues**
```bash
# Issue: Frontend not loading
# Solution: Check start.sh script and port 3000 availability

# Issue: API calls failing
# Solution: Verify NEXT_PUBLIC_API_URL is empty in production
```

#### **Database Connection**
```bash
# Issue: Database connection fails
# Solution: Verify DATABASE_URL format (postgresql:// not postgres://)

# Issue: Admin user not created
# Solution: Check startup logs for user creation process
```

### **Rollback Plan**
If issues occur:
1. **Keep old services** running during migration
2. **Test thoroughly** before switching traffic
3. **Have database backup** ready
4. **Document old configuration** for quick rollback

---

## 📊 Performance Comparison

### **Before (Dual-Service)**
- **Cold Start**: 15-30s (backend) + 5-10s (frontend)
- **CORS Overhead**: Additional preflight requests
- **Resource Usage**: Two separate containers
- **Complexity**: Multiple service monitoring

### **After (Unified)**
- **Cold Start**: 20-35s (single container startup)
- **No CORS Overhead**: Same-host requests
- **Resource Usage**: Single optimized container
- **Complexity**: Unified service monitoring

---

## ✅ Migration Checklist

### **Pre-Migration**
- [ ] **Backup current deployment** configuration
- [ ] **Export environment variables** from existing services
- [ ] **Test new deployment** in staging/development
- [ ] **Prepare rollback plan** if needed

### **During Migration**
- [ ] **Deploy new unified service** on Render
- [ ] **Configure environment variables** correctly
- [ ] **Link database** (existing or new)
- [ ] **Test all functionality** thoroughly

### **Post-Migration**
- [ ] **Verify application** works correctly
- [ ] **Update DNS** (if using custom domain)
- [ ] **Monitor performance** and logs
- [ ] **Clean up old services** when confident

### **Validation**
- [ ] **Health check**: `/health` endpoint responds
- [ ] **Frontend loads**: Application displays correctly
- [ ] **Authentication**: Login/logout works
- [ ] **API calls**: Dashboard and features functional
- [ ] **Styling**: Melbourne Celebrant branding intact
- [ ] **Performance**: Acceptable load times

---

## 🌐 URL Changes

### **Before Migration**
- **Frontend**: `https://your-app.vercel.app`
- **Backend API**: `https://your-backend.onrender.com`
- **API Docs**: `https://your-backend.onrender.com/docs`

### **After Migration**
- **Application**: `https://your-app.onrender.com`
- **API Docs**: `https://your-app.onrender.com/docs`
- **Health Check**: `https://your-app.onrender.com/health`

---

## 📞 Support During Migration

### **If Issues Arise**
1. **Check Render logs**: Dashboard → Service → Logs
2. **Verify environment variables**: All required vars set
3. **Test health endpoint**: Confirms backend is running
4. **Check Docker build**: Ensure build completes successfully

### **Resources**
- **Main Documentation**: `README.md`
- **Render Guide**: `RENDER_DEPLOYMENT.md`
- **Render Support**: [community.render.com](https://community.render.com)

---

🎉 **Migration to unified Render deployment provides a simpler, more cost-effective, and easier-to-manage solution for the Melbourne Celebrant Portal!** 