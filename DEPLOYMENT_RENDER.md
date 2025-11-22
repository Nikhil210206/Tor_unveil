# 🚀 Deployment Guide - Render

Complete guide to deploy your TOR Analysis Tool to Render (Backend) and Vercel (Frontend).

## 📋 Prerequisites

- GitHub account
- Render account (render.com)
- Vercel account (vercel.com)
- Your code pushed to GitHub

## 🔧 Step 1: Push to GitHub

```bash
cd /Users/nikhil/Documents/Tor_unveil

# Initialize git if not already done
git add .
git commit -m "Complete TOR analysis tool - ready for deployment"
git push origin main
```

## 🖥️ Step 2: Deploy Backend to Render

### A. Create Web Service

1. Go to https://render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select your `Tor_unveil` repository

### B. Configure Service

**Basic Settings:**
- **Name**: `tor-analysis-backend` (or your choice)
- **Region**: Choose closest to you
- **Branch**: `main`
- **Root Directory**: `backend`
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: 
  ```bash
  pip install -r requirements.txt -r requirements-api.txt
  ```

- **Start Command**:
  ```bash
  uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
  ```

**Instance Type:**
- Select **Free** tier (or paid if you need more resources)

### C. Environment Variables (Optional)

Click **"Advanced"** → **"Add Environment Variable"**:

- `PYTHON_VERSION`: `3.11.0`
- `DATABASE_URL`: `sqlite:///tor_analysis.db` (or PostgreSQL if you set it up)

### D. Deploy

1. Click **"Create Web Service"**
2. Wait for deployment (5-10 minutes)
3. Your backend will be at: `https://tor-analysis-backend.onrender.com`

### E. Test Backend

Once deployed, test:
```bash
curl https://tor-analysis-backend.onrender.com/api/stats
```

Should return JSON with stats.

Also visit: `https://tor-analysis-backend.onrender.com/docs`

## 🌐 Step 3: Deploy Frontend to Vercel

### A. Prepare Frontend

**Update API URL for production:**

Edit `frontend/src/lib/api.ts`:

```typescript
// Change from:
const API_BASE_URL = 'http://localhost:8000';

// To:
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

**Create environment file:**

Create `frontend/.env.production`:
```bash
VITE_API_URL=https://tor-analysis-backend.onrender.com
```

**Commit changes:**
```bash
git add frontend/src/lib/api.ts frontend/.env.production
git commit -m "Configure production API URL"
git push
```

### B. Deploy to Vercel

**Option 1: Vercel CLI**
```bash
cd /Users/nikhil/Documents/Tor_unveil/frontend
npm install -g vercel
vercel login
vercel
```

Follow prompts:
- Set root directory: `frontend`
- Framework: Vite
- Build command: `npm run build`
- Output directory: `dist`

**Option 2: Vercel Dashboard**

1. Go to https://vercel.com
2. Click **"Add New"** → **"Project"**
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Add Environment Variable:
   - **Name**: `VITE_API_URL`
   - **Value**: `https://tor-analysis-backend.onrender.com`
6. Click **"Deploy"**

### C. Your Frontend URL

After deployment: `https://tor-unveil.vercel.app` (or similar)

## 🔗 Step 4: Update CORS

**Important!** Update backend CORS to allow your frontend domain.

Edit `backend/src/api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Local development
        "https://tor-unveil.vercel.app",  # Your Vercel URL
        "https://*.vercel.app"  # All Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Commit and push:**
```bash
git add backend/src/api/main.py
git commit -m "Update CORS for production"
git push
```

Render will auto-redeploy.

## ✅ Step 5: Verify Deployment

### Test Backend:
```bash
curl https://tor-analysis-backend.onrender.com/api/stats
```

### Test Frontend:
1. Open `https://tor-unveil.vercel.app`
2. Check Dashboard loads
3. Try uploading a PCAP
4. Verify no CORS errors in browser console

## 📊 Step 6: Database Persistence (Important!)

**Issue:** Render free tier resets filesystem on restart, so SQLite data is lost.

**Solutions:**

### Option A: Use Render Disk (Paid)
Add persistent disk in Render dashboard:
- Go to your service
- **"Disks"** → **"Add Disk"**
- Mount path: `/data`
- Update database path in code to `/data/tor_analysis.db`

### Option B: Use PostgreSQL (Recommended for Production)

1. **Create PostgreSQL database on Render:**
   - Dashboard → **"New +"** → **"PostgreSQL"**
   - Free tier available
   - Copy the **Internal Database URL**

2. **Update backend code:**

Edit `backend/src/api/main.py`:
```python
import os

# Use PostgreSQL in production, SQLite in development
db_url = os.getenv('DATABASE_URL', 'sqlite:///tor_analysis.db')
db_manager = init_database(Path("tor_analysis.db") if 'sqlite' in db_url else db_url)
```

3. **Add environment variable in Render:**
   - `DATABASE_URL`: (paste your PostgreSQL URL)

4. **Update requirements:**
Add to `backend/requirements.txt`:
```
psycopg2-binary>=2.9.9
```

### Option C: Accept Data Loss (Demo Only)
For hackathon demos, it's okay if data resets. Just re-upload PCAP after each restart.

## 🎯 Final Checklist

- [ ] Backend deployed to Render
- [ ] Backend API accessible at `/api/stats`
- [ ] Frontend deployed to Vercel
- [ ] Frontend loads successfully
- [ ] CORS configured correctly
- [ ] Environment variables set
- [ ] Can upload PCAP and see results
- [ ] Database persistence configured (if needed)

## 🔄 Continuous Deployment

Both Render and Vercel support auto-deployment:

- **Push to `main` branch** → Both redeploy automatically
- **Create PR** → Vercel creates preview deployment
- **Merge PR** → Production updates

## 💡 Pro Tips

### Custom Domain (Optional)
- **Vercel**: Settings → Domains → Add custom domain
- **Render**: Settings → Custom Domain

### Monitoring
- **Render**: Built-in logs and metrics
- **Vercel**: Analytics dashboard

### Scaling
- **Render**: Upgrade to paid tier for more resources
- **Vercel**: Automatically scales

## 🐛 Troubleshooting

### Backend won't start
- Check Render logs
- Verify build command
- Check Python version
- Ensure all dependencies in requirements.txt

### Frontend can't connect to backend
- Check CORS settings
- Verify `VITE_API_URL` environment variable
- Check browser console for errors
- Test backend URL directly

### PCAP upload fails
- Check file size limits (Render free: 512MB)
- Verify backend has write permissions
- Check backend logs for errors

### Database resets
- Implement PostgreSQL (see Step 6)
- Or add persistent disk (paid)

## 📚 Resources

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **Your Backend**: https://tor-analysis-backend.onrender.com
- **Your Frontend**: https://tor-unveil.vercel.app

---

## 🚀 Quick Deploy Commands

```bash
# 1. Push to GitHub
git add .
git commit -m "Ready for deployment"
git push

# 2. Deploy frontend
cd frontend
vercel --prod

# 3. Backend deploys automatically on Render after GitHub push
```

**Your TOR Analysis Tool is now live!** 🎉
