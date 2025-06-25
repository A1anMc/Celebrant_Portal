# 🚀 Free Production Deployment Guide
## Melbourne Celebrant Portal - FastAPI + Next.js

This guide will deploy your full-stack application using **100% free** infrastructure:
- **Backend**: Render.com (Free tier)
- **Database**: Render PostgreSQL (Free tier)
- **Frontend**: Vercel (Free tier)
- **Domain**: Vercel subdomain (Free)
- **Email**: Brevo (Free tier - 300 emails/day)

---

## 📋 Prerequisites

1. GitHub account with your code pushed
2. Render.com account (free)
3. Vercel account (free)
4. Brevo.com account (free) for email

---

## 🗄️ Step 1: Deploy Database (Render PostgreSQL)

### 1.1 Create Database
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `melbourne-celebrant-db`
   - **Database**: `celebrant_portal`
   - **User**: `celebrant_user`
   - **Region**: Choose closest to your users
   - **PostgreSQL Version**: 15
   - **Plan**: **Free** ($0/month)

4. Click **"Create Database"**
5. Wait for deployment (2-3 minutes)
6. **Save the connection details** - you'll need them!

---

## 🖥️ Step 2: Deploy Backend (Render Web Service)

### 2.1 Create Web Service
1. In Render Dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - **Name**: `melbourne-celebrant-api`
   - **Region**: Same as database
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
   - **Plan**: **Free** ($0/month)

### 2.2 Set Environment Variables
In the **Environment** tab, add:

```bash
# Application
ENVIRONMENT=production
DEBUG=false

# Database (Get from your database dashboard)
DATABASE_URL=postgresql://celebrant_user:your_password@your_host/celebrant_portal

# Security (Generate a secure key)
SECRET_KEY=your-super-secure-secret-key-32-chars-min
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# Email (Brevo settings)
SMTP_HOST=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USERNAME=your-brevo-email@gmail.com
SMTP_PASSWORD=your-brevo-smtp-key
FROM_EMAIL=noreply@amelbournecelebrant.com.au

# File Upload
MAX_FILE_SIZE=10485760
UPLOAD_DIR=/tmp/uploads
```

### 2.3 Deploy
1. Click **"Create Web Service"**
2. Wait for build and deployment (5-10 minutes)
3. Your API will be available at: `https://melbourne-celebrant-api.onrender.com`
4. Test health check: `https://melbourne-celebrant-api.onrender.com/health`

---

## 🌐 Step 3: Deploy Frontend (Vercel)

### 3.1 Deploy to Vercel
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"New Project"**
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`

### 3.2 Set Environment Variables
In Vercel project settings → **Environment Variables**, add:

```bash
NEXT_PUBLIC_API_URL=https://melbourne-celebrant-api.onrender.com
NEXT_PUBLIC_APP_URL=https://your-app-name.vercel.app
NEXT_PUBLIC_APP_NAME=Melbourne Celebrant Portal
NEXT_PUBLIC_APP_VERSION=2.0.0
```

### 3.3 Deploy
1. Click **"Deploy"**
2. Wait for build (3-5 minutes)
3. Your app will be available at: `https://your-app-name.vercel.app`

---

## 📧 Step 4: Setup Email (Brevo)

### 4.1 Create Brevo Account
1. Sign up at [Brevo.com](https://www.brevo.com/)
2. Verify your email
3. Go to **SMTP & API** → **SMTP**
4. Get your SMTP credentials

### 4.2 Configure Email
1. **Login**: Your Brevo email
2. **Password**: Your SMTP key (not your login password)
3. **Server**: smtp-relay.brevo.com
4. **Port**: 587

Update your Render environment variables with these credentials.

---

## 🔐 Step 5: Security & CORS Update

### 5.1 Update Backend CORS
Your backend config already includes the correct CORS origins. If you use a custom domain, add it to the `allowed_origins` list in `backend/app/config.py`.

### 5.2 Generate Secure Secret Key
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Use this output as your `SECRET_KEY` in Render.

---

## ✅ Step 6: Verification Checklist

### 6.1 Backend Health Check
- [ ] Visit: `https://melbourne-celebrant-api.onrender.com/health`
- [ ] Should return: `{"status": "healthy"}`
- [ ] Visit: `https://melbourne-celebrant-api.onrender.com/docs`
- [ ] Should show FastAPI documentation

### 6.2 Database Connection
- [ ] Backend logs show successful database connection
- [ ] No database connection errors in Render logs

### 6.3 Frontend Functionality
- [ ] Visit your Vercel URL
- [ ] Landing page loads correctly
- [ ] Login form appears
- [ ] No console errors in browser dev tools

### 6.4 Full Stack Integration
- [ ] Create test account via API docs
- [ ] Login works from frontend
- [ ] Dashboard loads with data
- [ ] API calls work (check Network tab)

---

## 🛠️ Step 7: Create Admin User

### 7.1 Via API Documentation
1. Go to `https://melbourne-celebrant-api.onrender.com/docs`
2. Use **POST /api/auth/register** endpoint
3. Create admin user:
```json
{
  "email": "admin@amelbournecelebrant.com.au",
  "password": "YourSecurePassword123!",
  "full_name": "Alan McCarthy"
}
```

---

## 📊 Step 8: Optional Monitoring

### 8.1 UptimeRobot (Free)
1. Sign up at [UptimeRobot.com](https://uptimerobot.com/)
2. Add monitors for:
   - `https://melbourne-celebrant-api.onrender.com/health`
   - `https://your-app-name.vercel.app`

### 8.2 Render Logs
- Monitor your app health in Render Dashboard → Logs
- Set up email alerts for service failures

---

## 🚀 Step 9: Beta Launch Setup

### 9.1 Create Beta Signup Form
1. Create Airtable base or Google Form
2. Embed on your landing page
3. Collect: Name, Email, Business Name, Phone

### 9.2 Landing Page Updates
Update `frontend/src/app/page.tsx` with:
- Beta signup CTA
- Feature highlights
- Testimonials section
- Pricing preview

---

## 💰 Free Tier Limits

### Render Free Tier:
- ✅ 750 hours/month (enough for 24/7)
- ✅ PostgreSQL database (1GB storage)
- ⚠️ Sleeps after 15 min inactivity
- ⚠️ Cold starts (15-30 seconds)

### Vercel Free Tier:
- ✅ Unlimited bandwidth
- ✅ 100GB build output
- ✅ Custom domains
- ✅ Automatic HTTPS

### Brevo Free Tier:
- ✅ 300 emails/day
- ✅ Unlimited contacts
- ✅ Email templates

---

## 🔄 Continuous Deployment

Both Render and Vercel will automatically redeploy when you push to your `main` branch on GitHub.

---

## 🆘 Troubleshooting

### Backend Won't Start
1. Check Render logs for Python errors
2. Verify all environment variables are set
3. Ensure `requirements.txt` includes all dependencies

### Frontend API Errors
1. Check CORS settings in backend
2. Verify `NEXT_PUBLIC_API_URL` is correct
3. Check browser console for network errors

### Database Connection Issues
1. Verify `DATABASE_URL` format
2. Check database is running in Render
3. Test connection from backend logs

---

## 📈 Next Steps (Post-Launch)

1. **Custom Domain**: Point your domain to Vercel
2. **Email Domain**: Set up email forwarding
3. **Analytics**: Add Google Analytics or Plausible
4. **Monitoring**: Set up error tracking with Sentry
5. **Backups**: Enable automatic database backups
6. **CDN**: Leverage Vercel's global CDN

---

## 💡 Pro Tips

1. **Keep Render Warm**: Set up a cron job to ping your API every 10 minutes
2. **Environment Sync**: Keep dev and prod environment variables in sync
3. **Database Migrations**: Run migrations via Render console when needed
4. **Logs**: Regularly check both Render and Vercel logs
5. **Security**: Regularly rotate your SECRET_KEY

---

🎉 **Congratulations!** Your Melbourne Celebrant Portal is now live and ready for beta users!

**Live URLs:**
- Frontend: `https://your-app-name.vercel.app`
- API: `https://melbourne-celebrant-api.onrender.com`
- API Docs: `https://melbourne-celebrant-api.onrender.com/docs` 