# 🐵 Zhizhongcao - GitHub Remote Repository Setup Instructions

**Date:** 2026-03-26  
**Time:** 08:12 AM  
**Urgency:** 🔥 CRITICAL  

---

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. **Repository name:** `zhizhongcao`
3. **Description:** AI-powered Q&A and Xiaohongshu auto-publishing platform | 智种草 - AI 问答种草自动发文工具
4. **Visibility:** Public (for demo purposes) or Private
5. ✅ Add README (skip, we already have one)
6. Click **"Create repository"**

---

## Step 2: Push Code to Remote

```bash
cd C:\Users\Administrator\.openclaw\workspace\zhizhongcao

# Add remote origin (replace YOUR_USERNAME with your GitHub username)
git remote add origin git@github.com:YOUR_USERNAME/zhizhongcao.git

# Or use HTTPS if SSH not configured:
# git remote add origin https://github.com/YOUR_USERNAME/zhizhongcao.git

# Verify
git remote -v

# Push to main branch
git push -u origin main
```

---

## Step 3: Deploy to Railway.app

After pushing to GitHub:

1. Go to https://railway.app
2. Sign in with GitHub
3. Click **"New Project"** → **"Deploy from GitHub repo"**
4. Select `zhizhongcao` repository
5. Railway will auto-detect Python + FastAPI
6. Click **"Deploy"**
7. Wait ~5 minutes for build
8. Get public URL: `https://zhizhongcao.up.railway.app`

---

## Step 4: Update Frontend API URLs

Once Railway gives you the public URL, update:

`zhizhongcao/frontend/signup.html`:

```javascript
// Change from:
const API_BASE = 'http://localhost:8000';

// To:
const API_BASE = 'https://zhizhongcao-backend.up.railway.app';
```

---

## Alternative: Vercel Deployment

If Railway doesn't work:

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy backend to Render (free tier)
# Frontend to Vercel
vercel deploy --prod

# Get public URL from Vercel dashboard
```

---

## Expected Timeline

| Action | Time | Status |
|--------|------|--------|
| Create GitHub repo | 08:15 | → Pending |
| Push to remote | 08:20 | → Pending |
| Railway deploy start | 08:25 | → Pending |
| Get public URL | 08:30 | → Goal! |
| Update frontend URLs | 08:35 | → Pending |
| Test public access | 08:40 | → Pending |
| Start seed user outreach | 08:45 | → Ready! |

---

_Ready to execute once you provide GitHub username or create repo!_
