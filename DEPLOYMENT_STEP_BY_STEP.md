# 🎯 Step-by-Step Render Deployment Guide

## 📝 Prerequisites Checklist

- [x] Code pushed to GitHub ✅
- [ ] Render account created
- [ ] Backend deployed
- [ ] Frontend deployed

## 🚀 Part 1: Deploy Backend to Render

### Step 1: Create Render Account

1. Go to https://render.com
2. Click **"Get Started"** or **"Sign Up"**
3. Sign up with GitHub (recommended) or email
4. Verify your email if needed

### Step 2: Create New Web Service

1. After logging in, you'll see the Render Dashboard
2. Click the **"New +"** button (top right)
3. Select **"Web Service"** from the dropdown

### Step 3: Connect GitHub Repository

1. If first time: Click **"Connect GitHub"**
   - Authorize Render to access your GitHub
   - You may need to install Render app on GitHub
2. Search for your repository: `Tor_unveil`
3. Click **"Connect"** next to your repository

### Step 4: Configure Web Service

Fill in the form with these EXACT values:

**Basic Info:**
```
Name: tor-analysis-backend
Region: Oregon (US West) or closest to you
Branch: main
```

**Build Settings:**
```
Root Directory: backend
Runtime: Python 3
```

**Build Command:**
```
pip install -r requirements.txt -r requirements-api.txt
```

**Start Command:**
```
uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
```

**Instance Type:**
```
Free (or select paid if you need more resources)
```

### Step 5: Advanced Settings (Optional)

Click **"Advanced"** to add environment variables:

```
PYTHON_VERSION = 3.11.0
```

### Step 6: Create Web Service

1. Review all settings
2. Click **"Create Web Service"** button at the bottom
3. Wait for deployment (5-10 minutes)

### Step 7: Monitor Deployment

You'll see a build log showing:
```
==> Cloning from https://github.com/Nikhil210206/Tor_unveil...
==> Installing dependencies...
==> Starting server...
==> Your service is live 🎉
```

### Step 8: Get Your Backend URL

Once deployed, you'll see:
```
https://tor-analysis-backend.onrender.com
```

Copy this URL - you'll need it for the frontend!

### Step 9: Test Your Backend

Open a new terminal and test:

```bash
# Test the API
curl https://tor-analysis-backend.onrender.com/api/stats

# Should return JSON like:
# {"total_flows":0,"suspect_flows":0,...}
```

Or visit in browser:
```
https://tor-analysis-backend.onrender.com/docs
```

You should see the FastAPI Swagger documentation!

---

## 🌐 Part 2: Deploy Frontend to Vercel

### Step 1: Update Frontend API URL

Before deploying, update the API URL:

**Edit `frontend/src/lib/api.ts`:**

```typescript
// Change line 1 from:
const API_BASE_URL = 'http://localhost:8000';

// To:
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://tor-analysis-backend.onrender.com';
```

**Commit and push:**
```bash
cd /Users/nikhil/Documents/Tor_unveil
git add frontend/src/lib/api.ts
git commit -m "Update API URL for production"
git push origin main
```

### Step 2: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 3: Login to Vercel

```bash
vercel login
```

Choose your login method (GitHub recommended).

### Step 4: Deploy Frontend

```bash
cd /Users/nikhil/Documents/Tor_unveil/frontend
vercel
```

**Answer the prompts:**

```
? Set up and deploy "~/Documents/Tor_unveil/frontend"? [Y/n] y
? Which scope do you want to deploy to? Your Name
? Link to existing project? [y/N] n
? What's your project's name? tor-unveil-frontend
? In which directory is your code located? ./
? Want to override the settings? [y/N] n
```

Vercel will:
1. Build your frontend
2. Deploy it
3. Give you a URL like: `https://tor-unveil-frontend.vercel.app`

### Step 5: Set Environment Variable

```bash
vercel env add VITE_API_URL
```

When prompted, enter:
```
https://tor-analysis-backend.onrender.com
```

Select: `Production`, `Preview`, `Development` (all three)

### Step 6: Redeploy with Environment Variable

```bash
vercel --prod
```

---

## 🔗 Part 3: Update CORS

### Step 1: Update Backend CORS

**Edit `backend/src/api/main.py`:**

Find the CORS middleware section and update:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local development
        "https://tor-unveil-frontend.vercel.app",  # Your Vercel URL
        "https://*.vercel.app"  # All Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 2: Push Changes

```bash
cd /Users/nikhil/Documents/Tor_unveil
git add backend/src/api/main.py
git commit -m "Update CORS for production"
git push origin main
```

Render will automatically redeploy!

---

## ✅ Part 4: Verify Everything Works

### Test Backend:
```bash
curl https://tor-analysis-backend.onrender.com/api/stats
```

### Test Frontend:
1. Open `https://tor-unveil-frontend.vercel.app`
2. Dashboard should load
3. Open browser DevTools (F12) → Console
4. Should see no CORS errors
5. Stats should load from backend

### Test Full Flow:
1. Go to Upload page
2. Upload the sample PCAP you downloaded
3. Click "Analyze"
4. Check Dashboard for results
5. View Flows, Graph, Timeline
6. Generate a report

---

## 🎉 You're Live!

**Your URLs:**
- Backend API: `https://tor-analysis-backend.onrender.com`
- Backend Docs: `https://tor-analysis-backend.onrender.com/docs`
- Frontend App: `https://tor-unveil-frontend.vercel.app`

---

## 🐛 Troubleshooting

### Backend won't deploy?
- Check Render logs for errors
- Verify `requirements.txt` and `requirements-api.txt` exist in `backend/`
- Make sure `backend/src/api/main.py` exists

### Frontend can't connect?
- Check CORS settings in backend
- Verify `VITE_API_URL` environment variable in Vercel
- Check browser console for errors

### "Module not found" errors?
- Make sure root directory is set to `backend` in Render
- Check that all `__init__.py` files exist

---

## 📱 Share Your Project

Once deployed, share these links:
- **Live App**: https://tor-unveil-frontend.vercel.app
- **API Docs**: https://tor-analysis-backend.onrender.com/docs
- **GitHub**: https://github.com/Nikhil210206/Tor_unveil

---

## 🔄 Future Updates

To update your deployed app:

```bash
# Make changes locally
git add .
git commit -m "Your changes"
git push origin main
```

Both Render and Vercel will auto-deploy! 🚀

---

**Need help? Check the logs:**
- Render: Dashboard → Your Service → Logs
- Vercel: Dashboard → Your Project → Deployments → View Logs
