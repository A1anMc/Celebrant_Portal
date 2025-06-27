# 🚀 Frontend Deployment Guide

## ✅ Current Status
- **Backend**: ✅ Working at https://amelbournecelebrant-6ykh.onrender.com
- **Frontend**: ❌ Needs separate deployment

## 🎯 Quick Solution: Deploy Frontend to Vercel

### Step 1: Prepare the Frontend
```bash
cd celebrant-portal-v2/frontend
```

### Step 2: Create Environment File
Create `.env.local`:
```
NEXT_PUBLIC_API_URL=https://amelbournecelebrant-6ykh.onrender.com
```

### Step 3: Deploy to Vercel
1. Go to [vercel.com](https://vercel.com)
2. Sign in with GitHub
3. Click "New Project"
4. Import your GitHub repository
5. Set **Root Directory** to: `celebrant-portal-v2/frontend`
6. Add environment variable:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://amelbournecelebrant-6ykh.onrender.com`
7. Click "Deploy"

### Step 4: Access Your App
- Frontend will be at: `https://your-project.vercel.app`
- Backend API at: `https://amelbournecelebrant-6ykh.onrender.com`

## 🔧 Alternative: Test Locally
```bash
cd celebrant-portal-v2/frontend
npm install
NEXT_PUBLIC_API_URL=https://amelbournecelebrant-6ykh.onrender.com npm run dev
```

Your app will be at `http://localhost:3000` connecting to the live backend!

---

**Current Backend API Response**: 
```json
{"message":"Melbourne Celebrant Portal API","version":"2.0.0","status":"running","environment":"production"}
```

This means your backend is working perfectly! 🎉 