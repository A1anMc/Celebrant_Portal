# Render Deployment Fix: passlib Import Error

## Problem
FastAPI backend deployment failing on Render with:
```
ImportError: No module named 'passlib'
```

## Root Cause Analysis
Despite `passlib[bcrypt]==1.7.4` being listed in `requirements.txt`, Render's build process is not installing it correctly.

## ✅ Solutions Implemented

### 1. Verified Requirements.txt
- ✅ `passlib[bcrypt]==1.7.4` is correctly listed in `/celebrant-portal-v2/backend/requirements.txt`
- ✅ All critical dependencies are present:
  - `fastapi==0.115.6`
  - `uvicorn[standard]==0.32.1`
  - `passlib[bcrypt]==1.7.4`
  - `PyJWT==2.10.1`
  - `sqlalchemy==2.0.36`
  - `pydantic==2.10.3`

### 2. Enhanced Import Testing
- ✅ Updated `test_imports.py` with comprehensive dependency checks
- ✅ Added specific passlib version validation
- ✅ All imports working locally: `passlib version: 1.7.4`

### 3. Fixed Render Configuration
- ✅ Created proper `render.yaml` in `/celebrant-portal-v2/backend/`
- ✅ Updated build command: `pip install --upgrade pip && pip install -r requirements.txt`
- ✅ Added import validation to start command

### 4. Deployment Validation Script
- ✅ Created `deploy_render.py` for pre-deployment validation
- ✅ All local tests passing

## 🚀 Deployment Instructions

### For Render Dashboard:
1. **Repository**: Connect to your GitHub repository
2. **Root Directory**: Set to `celebrant-portal-v2/backend`
3. **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
4. **Start Command**: `python test_imports.py && gunicorn app.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`

### Environment Variables:
```
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=[auto-generated]
DATABASE_URL=[from database]
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30
```

## 🧹 If Still Failing - Clean Build Steps:

1. **Clear Render Cache**:
   - Go to Render Dashboard
   - Select your service
   - Settings → Clear build cache
   - Redeploy

2. **Verify Directory Structure**:
   ```
   celebrant-portal-v2/
   └── backend/
       ├── requirements.txt  ← Must be here
       ├── render.yaml       ← Must be here
       ├── app/
       └── test_imports.py
   ```

3. **Manual Build Test**:
   ```bash
   cd celebrant-portal-v2/backend
   python test_imports.py
   python deploy_render.py
   ```

## 🔍 Debugging Steps:

1. **Check Render Build Logs** for:
   - `pip install -r requirements.txt` output
   - Any package installation errors
   - Python version compatibility

2. **Verify Requirements File Location**:
   - Render must find `requirements.txt` in the root directory
   - Current location: `/celebrant-portal-v2/backend/requirements.txt`

3. **Test Import Command**:
   - Add to Render start command: `python -c "import passlib; print('passlib OK')" && `

## 📋 Final Checklist:
- ✅ `passlib[bcrypt]==1.7.4` in requirements.txt
- ✅ Render root directory set to `celebrant-portal-v2/backend`
- ✅ Build command includes `pip install --upgrade pip`
- ✅ Start command includes import validation
- ✅ All environment variables configured
- ✅ Database connection configured

## 🆘 Emergency Fix:
If still failing, try this minimal start command:
```
python -c "import sys; print(sys.path)" && pip list | grep passlib && gunicorn app.main:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

This will show you exactly what's happening with the Python environment and package installation. 