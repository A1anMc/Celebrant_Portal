# 🚨 CRITICAL FIX: Vercel Environment Variable

## **The Problem**
Your Vercel deployment is failing because the frontend can't connect to your backend. The environment variable `NEXT_PUBLIC_API_URL` is not set in Vercel.

## **The Solution (5 minutes)**

### **Step 1: Get Your Backend URL**
Your Render backend URL is likely:
```
https://melbourne-celebrant-portal-backend.onrender.com
```

### **Step 2: Set Environment Variable in Vercel**
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click on your project
3. Go to **Settings** → **Environment Variables**
4. Click **Add New**
5. Set:
   - **Name**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://melbourne-celebrant-portal-backend.onrender.com`
   - **Environment**: Production, Preview, Development
6. Click **Save**

### **Step 3: Redeploy**
1. Go to **Deployments** tab
2. Click **Redeploy** on your latest deployment
3. Wait 2-3 minutes

## **Why This Fixes It**
- Your Next.js config now uses `process.env.NEXT_PUBLIC_API_URL`
- Without this variable, API calls fail
- This is why Vercel shows "Deployment has failed"

## **Expected Result**
✅ Vercel deployment succeeds
✅ Frontend connects to backend
✅ Your app works in production

**This should fix your immediate deployment issue!** 🚀
