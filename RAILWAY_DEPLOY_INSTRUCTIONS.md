# 🐵 Zhizhongcao - Railway Deployment Steps

**Time:** 08:54 AM  
**Repository:** https://github.com/billycool2005/zhizhongcao  

---

## Step 1: Go to Railway.app

Visit: https://railway.app

## Step 2: Sign in with GitHub

- Click "Sign in with GitHub"
- Authorize Railway access
- Select user: `billycool2005`

## Step 3: Create New Project from Repo

1. Click **"New Project"**
2. Choose **"Deploy from GitHub repo"**
3. Find and select: `billycool2005/zhizhongcao`
4. Click **"Deploy"**

## Step 4: Configure Environment Variables

Add these to Railway's environment:

```
DATABASE_URL=postgresql://user:password@db:5432/zhizhongcao
REDIS_URL=redis://redis:6379/0
QWEN_API_KEY=[your_qwen_api_key]
SECRET_KEY=super-secret-key-change-in-production
APP_ENV=production
DEBUG=False
ALLOWED_ORIGINS=https://*.railway.app
```

## Step 5: Deploy & Get Public URL

- Railway will auto-detect Python + FastAPI
- Build takes ~3-5 minutes
- **Public URL will be shown:** `https://zhizhongcao.up.railway.app`

---

## Alternative: Vercel if Railway Fails

```bash
npm i -g vercel
cd frontend
vercel deploy --prod

cd ../backend
render create project zhizhongcao-backend
render deploy
```

---

Expected Time: **5 minutes**
Target URL Ready by: **09:00 AM**
