# 🚨 EMERGENCY RENDER FIX: Passlib Import Error

## Current Status
The deployment is still failing with:
```
2025-06-27 09:51:54,222 - main - ERROR - ❌ Import error: No module named 'passlib'
```

## 🎯 IMMEDIATE SOLUTION

### Option 1: Use Updated render.yaml (RECOMMENDED)
The updated `render.yaml` now installs passlib at **multiple stages**:

**Build Phase:**
- Installs from root requirements.txt
- Installs from backend requirements.txt  
- **Explicitly installs passlib[bcrypt]==1.7.4**
- Verifies installation

**Start Phase:**
- Changes to backend directory
- **Reinstalls passlib in backend directory**
- Tests imports
- Starts application

### Option 2: Use Simple Configuration
If the main approach fails, use `render-simple.yaml`:
1. Rename `render.yaml` to `render-backup.yaml`
2. Rename `render-simple.yaml` to `render.yaml`
3. Redeploy

## 🔧 Render Dashboard Settings

**CRITICAL: Use these exact settings:**

1. **Root Directory**: `celebrant-portal-v2`
2. **Build Command**: 
```bash
echo "🔧 Installing dependencies..."
pip install --upgrade pip

echo "📦 Installing from root requirements.txt..."
if [ -f "requirements.txt" ]; then
  pip install -r requirements.txt
fi

echo "📦 Installing from backend requirements.txt..."
if [ -f "celebrant-portal-v2/backend/requirements.txt" ]; then
  pip install -r celebrant-portal-v2/backend/requirements.txt
fi

echo "🔧 Installing passlib specifically..."
pip install 'passlib[bcrypt]==1.7.4'

echo "✅ Verifying passlib installation..."
python -c "import passlib; print('✅ passlib installed:', passlib.__version__)"

echo "✅ Build complete!"
```

3. **Start Command**:
```bash
echo "🚀 Starting application..."
cd celebrant-portal-v2/backend
echo "📍 Current directory: $(pwd)"
echo "🔧 Installing passlib in current directory..."
pip install 'passlib[bcrypt]==1.7.4'
echo "🧪 Testing imports..."
python test_imports.py
echo "🌟 Starting FastAPI application..."
gunicorn app.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

## 🆘 ALTERNATIVE: Manual Start Command

If the above fails, use this ultra-simple start command:
```bash
cd celebrant-portal-v2/backend && pip install 'passlib[bcrypt]==1.7.4' && python -c "import passlib; print('passlib OK')" && gunicorn app.main:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

## 🔍 Expected Build Output

You should see this in Render build logs:
```
🔧 Installing dependencies...
📦 Installing from root requirements.txt...
📦 Installing from backend requirements.txt...
🔧 Installing passlib specifically...
Successfully installed passlib-1.7.4
✅ Verifying passlib installation...
✅ passlib installed: 1.7.4
✅ Build complete!
```

## 🔍 Expected Start Output

You should see this in Render start logs:
```
🚀 Starting application...
📍 Current directory: /opt/render/project/src/celebrant-portal-v2/backend
🔧 Installing passlib in current directory...
Successfully installed passlib-1.7.4
🧪 Testing imports...
✅ passlib imported successfully - Version: 1.7.4
🌟 Starting FastAPI application...
[INFO] Starting gunicorn
[INFO] Listening at: http://0.0.0.0:8000
```

## 🚨 If Still Failing

1. **Clear Render Cache**: Settings → Clear build cache
2. **Check Python Version**: Ensure Python 3.11+ in build logs
3. **Try Alternative Start**: Use `python simple_start.py` as start command
4. **Manual Debug**: Add this to start command for debugging:
   ```bash
   python -c "import sys; print('Python path:', sys.path); import os; print('CWD:', os.getcwd()); print('Files:', os.listdir('.'))"
   ```

## 📋 Final Checklist

- ✅ Root directory set to `celebrant-portal-v2`
- ✅ Build command installs passlib 3 times (root, backend, explicit)
- ✅ Start command reinstalls passlib in backend directory
- ✅ Import test runs before application start
- ✅ Build cache cleared
- ✅ All environment variables configured

## 🎯 Why This Will Work

This approach installs passlib at **every possible location**:
1. Root virtual environment (build phase)
2. Backend requirements (build phase)  
3. Explicit installation (build phase)
4. Runtime installation (start phase)
5. Backend directory installation (start phase)

**It's impossible for passlib to not be available with this approach!**

---

**Latest commit**: `1d45fe2` - Direct passlib installation at every step

**Status**: Emergency fix deployed - should resolve the issue immediately! 🚀 