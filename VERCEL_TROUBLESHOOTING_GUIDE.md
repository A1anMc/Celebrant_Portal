# 🚀 Vercel Deployment Troubleshooting Guide

## **Overview**
This guide provides systematic approaches to fix common Vercel deployment issues, especially for monorepo structures like the Melbourne Celebrant Portal.

## **🔍 Common Vercel Errors & Solutions**

### **Error 1: "cd frontend: No such file or directory"**

#### **Root Cause:**
- Vercel is trying to run commands from the root directory
- The Next.js app is in a subdirectory (`frontend/`)
- Vercel doesn't know where to find the app

#### **Solution 1: Root Directory Configuration**
```json
// vercel.json (in root)
{
  "version": 2,
  "framework": "nextjs",
  "rootDirectory": "frontend"
}
```

#### **Solution 2: Monorepo with Workspaces**
```json
// package.json (in root)
{
  "name": "melbourne-celebrant-portal",
  "version": "1.0.0",
  "private": true,
  "workspaces": [
    "frontend"
  ]
}
```

#### **Solution 3: Custom Build Script**
```bash
#!/bin/bash
# build.sh (in root)
cd frontend
npm install
npm run build
```

### **Error 2: "Build command failed"**

#### **Root Cause:**
- Missing dependencies
- Incorrect Node.js version
- Build script errors

#### **Solution:**
```json
// vercel.json
{
  "version": 2,
  "framework": "nextjs",
  "rootDirectory": "frontend",
  "buildCommand": "npm run build",
  "installCommand": "npm install"
}
```

### **Error 3: "Environment variables not found"**

#### **Root Cause:**
- Missing environment variables in Vercel dashboard
- Incorrect variable names

#### **Solution:**
1. Go to Vercel Dashboard → Project Settings → Environment Variables
2. Add required variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
   NEXT_PUBLIC_APP_NAME=Melbourne Celebrant Portal
   ```

### **Error 4: "Framework not detected"**

#### **Root Cause:**
- Vercel can't detect Next.js framework
- Missing or incorrect configuration

#### **Solution:**
```json
// vercel.json
{
  "version": 2,
  "framework": "nextjs",
  "rootDirectory": "frontend"
}
```

## **🎯 Systematic Troubleshooting Approach**

### **Step 1: Verify Project Structure**
```bash
# Check if frontend directory exists
ls -la frontend/

# Verify Next.js files exist
ls -la frontend/package.json
ls -la frontend/next.config.js
```

### **Step 2: Test Local Build**
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Test build locally
npm run build
```

### **Step 3: Check Vercel Configuration**
```bash
# Verify vercel.json exists and is correct
cat vercel.json

# Check for syntax errors
node -e "console.log(JSON.parse(require('fs').readFileSync('vercel.json')))"
```

### **Step 4: Environment Variables**
```bash
# Check if environment variables are set
vercel env ls

# Add missing variables
vercel env add NEXT_PUBLIC_API_URL
```

## **🔧 Advanced Fixes**

### **Fix 1: Force Redeploy**
```bash
# Clear Vercel cache and redeploy
vercel --force

# Or from dashboard: Settings → General → Clear Build Cache
```

### **Fix 2: Custom Build Configuration**
```json
// vercel.json
{
  "version": 2,
  "framework": "nextjs",
  "rootDirectory": "frontend",
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/.next"
}
```

### **Fix 3: Ignore Files**
```bash
# .vercelignore
backend/
*.md
.git/
.github/
scripts/
```

### **Fix 4: Debug Build Process**
```bash
# Enable verbose logging
vercel --debug

# Check build logs in Vercel dashboard
# Go to Deployments → Latest → View Build Logs
```

## **📋 Pre-Deployment Checklist**

### **Before Pushing to Vercel:**
- [ ] **Local build works**: `cd frontend && npm run build`
- [ ] **Dependencies installed**: `npm install` completes without errors
- [ ] **Environment variables ready**: All `NEXT_PUBLIC_*` variables defined
- [ ] **Configuration files correct**: `vercel.json` and `package.json` are valid
- [ ] **No syntax errors**: TypeScript compilation passes
- [ ] **No linting errors**: ESLint passes

### **Configuration Files:**
- [ ] **Root `vercel.json`** exists with `rootDirectory: "frontend"`
- [ ] **Root `package.json`** has proper workspace configuration
- [ ] **Frontend `package.json`** has correct scripts and dependencies
- [ ] **`.vercelignore`** excludes unnecessary files

## **🚨 Emergency Fixes**

### **Quick Fix 1: Minimal Configuration**
```json
// vercel.json
{
  "version": 2,
  "framework": "nextjs",
  "rootDirectory": "frontend"
}
```

### **Quick Fix 2: Remove All Custom Config**
```bash
# Delete all custom configuration
rm vercel.json
rm .vercelignore
rm build.sh

# Let Vercel auto-detect
```

### **Quick Fix 3: Manual Deployment**
```bash
# Deploy manually from frontend directory
cd frontend
vercel --prod
```

## **📊 Debugging Commands**

### **Check Vercel Status**
```bash
# Check Vercel CLI version
vercel --version

# Check project status
vercel ls

# Check deployment status
vercel ls --prod
```

### **Analyze Build Logs**
```bash
# Download build logs
vercel logs [deployment-url]

# Check specific deployment
vercel inspect [deployment-url]
```

### **Test Environment**
```bash
# Test environment variables
vercel env pull .env.local

# Verify variables are loaded
node -e "console.log(process.env.NEXT_PUBLIC_API_URL)"
```

## **🎯 Best Practices**

### **1. Keep Configuration Simple**
- Use minimal `vercel.json` configuration
- Let Vercel auto-detect when possible
- Avoid complex build scripts

### **2. Test Locally First**
- Always test builds locally before deploying
- Use `npm run build` in frontend directory
- Check for TypeScript/ESLint errors

### **3. Use Environment Variables**
- Store configuration in environment variables
- Use `NEXT_PUBLIC_*` prefix for client-side variables
- Never commit secrets to repository

### **4. Monitor Deployments**
- Check build logs for errors
- Monitor deployment status
- Set up notifications for failures

### **5. Version Control**
- Commit configuration changes
- Use descriptive commit messages
- Tag successful deployments

## **🔍 Common Patterns**

### **Pattern 1: Monorepo with Subdirectory**
```
project/
├── vercel.json          # rootDirectory: "frontend"
├── package.json         # workspaces: ["frontend"]
├── frontend/
│   ├── package.json     # Next.js app
│   ├── next.config.js
│   └── src/
└── backend/
    └── ...
```

### **Pattern 2: Standalone Next.js App**
```
project/
├── package.json         # Next.js app
├── next.config.js
├── src/
└── ...
```

### **Pattern 3: Custom Build Process**
```
project/
├── vercel.json          # custom buildCommand
├── build.sh            # custom build script
├── frontend/
│   └── ...
└── ...
```

## **🎉 Success Indicators**

### **Deployment Success:**
- ✅ Build completes without errors
- ✅ Application loads in browser
- ✅ Environment variables work
- ✅ API calls succeed
- ✅ No console errors

### **Configuration Success:**
- ✅ Vercel detects Next.js framework
- ✅ Build process runs in correct directory
- ✅ Dependencies install correctly
- ✅ Output directory is correct

## **📞 Getting Help**

### **Vercel Resources:**
- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Community](https://github.com/vercel/vercel/discussions)
- [Vercel Support](https://vercel.com/support)

### **Debugging Tools:**
- Vercel CLI: `npm i -g vercel`
- Vercel Dashboard: Build logs and deployment status
- Browser DevTools: Console errors and network requests

---

**Remember: Most Vercel issues can be solved by simplifying the configuration and ensuring the local build works first!** 🚀
