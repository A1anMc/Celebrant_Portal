# 🚀 Deployment Checklist - Melbourne Celebrant Portal

## ✅ Ready to Deploy Now!

Your production-ready Melbourne Celebrant Portal is configured and ready for free deployment.

---

## 🗄️ Step 1: Deploy Database (5 minutes)

1. **Go to [Render.com](https://dashboard.render.com/)**
2. **Create PostgreSQL Database:**
   - Name: `melbourne-celebrant-db`
   - Database: `celebrant_portal`  
   - User: `celebrant_user`
   - Plan: **Free**
3. **Save Database URL** (you'll need it next)

---

## 🖥️ Step 2: Deploy Backend (10 minutes)

1. **Create Render Web Service:**
   - Repository: `https://github.com/A1anMc/amelbournecelebrant.git`
   - Branch: `main`
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app.main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
   - Plan: **Free**

2. **Set Environment Variables:**
```bash
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=oav542oj7_XvU5sW8o-ypCZ_hTpyQ9EWLBmgku1v1Jk
DATABASE_URL=[paste your database URL from step 1]
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30
```

3. **Deploy and Test:**
   - Wait for build completion
   - Test: `https://your-backend-url.onrender.com/health`

---

## 🌐 Step 3: Deploy Frontend (5 minutes)

1. **Go to [Vercel.com](https://vercel.com/dashboard)**
2. **Import GitHub Repository:**
   - Repository: `https://github.com/A1anMc/amelbournecelebrant.git`
   - Framework: Next.js
   - Root Directory: `frontend`

3. **Set Environment Variables:**
```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.onrender.com
NEXT_PUBLIC_APP_URL=https://your-frontend-url.vercel.app
NEXT_PUBLIC_APP_NAME=Melbourne Celebrant Portal
```

4. **Deploy and Test:**
   - Wait for build completion
   - Visit your Vercel URL

---

## 📧 Step 4: Setup Email (Optional - 5 minutes)

1. **Sign up at [Brevo.com](https://www.brevo.com/)**
2. **Get SMTP credentials from dashboard**
3. **Add to Render environment variables:**
```bash
SMTP_HOST=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USERNAME=your-brevo-email
SMTP_PASSWORD=your-brevo-smtp-key
FROM_EMAIL=noreply@amelbournecelebrant.com.au
```

---

## ✅ Verification (2 minutes)

### Backend Health Check:
- [ ] `https://your-backend.onrender.com/health` returns `{"status": "healthy"}`
- [ ] `https://your-backend.onrender.com/docs` shows API documentation

### Frontend Check:
- [ ] Landing page loads with Melbourne Celebrant branding
- [ ] Beta signup page works: `/beta`
- [ ] Login page loads: `/login`

### Full Integration:
- [ ] Create admin user via API docs
- [ ] Login works from frontend
- [ ] Dashboard loads (may be empty initially)

---

## 🎯 Post-Deployment (Optional)

### Custom Domain (Free):
1. **In Vercel:** Settings → Domains → Add your domain
2. **Update DNS:** Point CNAME to `cname.vercel-dns.com`

### Monitoring (Free):
1. **[UptimeRobot.com](https://uptimerobot.com/)** - Monitor uptime
2. **Render Dashboard** - Check logs and metrics

### Beta Launch:
1. **Test beta signup form** at `/beta`
2. **Share beta URL** with potential users
3. **Monitor signups** (currently saves to form state)

---

## 🔗 Your Live URLs

After deployment, you'll have:

- **Frontend:** `https://your-app-name.vercel.app`
- **Backend API:** `https://your-backend-name.onrender.com`
- **API Documentation:** `https://your-backend-name.onrender.com/docs`
- **Beta Signup:** `https://your-app-name.vercel.app/beta`

---

## 💰 Monthly Costs: $0

- ✅ Render Free: 750 hours (24/7 coverage)
- ✅ Vercel Free: Unlimited bandwidth
- ✅ Brevo Free: 300 emails/day
- ✅ Domain: Free Vercel subdomain

---

## 🆘 Need Help?

1. **Check the detailed guide:** `DEPLOYMENT_GUIDE_FREE.md`
2. **Render logs:** Dashboard → Your Service → Logs
3. **Vercel logs:** Dashboard → Your Project → Functions
4. **Common issues:** CORS errors = check environment variables

---

🎉 **Total Deployment Time: ~25 minutes**

Your Melbourne Celebrant Portal will be live and ready for beta users! 