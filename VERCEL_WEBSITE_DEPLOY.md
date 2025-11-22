# 🌐 Deploy Frontend via Vercel Website (Easiest Method!)

## ✅ Step 1: Push Your Changes to GitHub

First, commit the API URL change:

```bash
cd /Users/nikhil/Documents/Tor_unveil
git add frontend/src/lib/api.ts
git commit -m "Update API URL to production backend"
git push origin main
```

---

## 🚀 Step 2: Deploy on Vercel Website

### 1. Go to Vercel
Visit: https://vercel.com

### 2. Sign Up/Login
- Click **"Sign Up"** or **"Login"**
- Choose **"Continue with GitHub"** (easiest)
- Authorize Vercel to access your GitHub

### 3. Import Your Project
- Click **"Add New..."** → **"Project"**
- You'll see your GitHub repositories
- Find and click **"Import"** next to `Tor_unveil`

### 4. Configure Project

**Framework Preset:**
- Vercel should auto-detect: **Vite**
- If not, select **"Vite"** from dropdown

**Root Directory:**
- Click **"Edit"** next to Root Directory
- Enter: `frontend`
- Click **"Continue"**

**Build Settings (Auto-detected):**
- Build Command: `npm run build`
- Output Directory: `dist`
- Install Command: `npm install`

**Leave these as default - Vercel knows what to do!**

### 5. Add Environment Variable

Click **"Environment Variables"** section:

- **Name**: `VITE_API_URL`
- **Value**: `https://tor-unveil-dil6.onrender.com`
- Click **"Add"**

### 6. Deploy!

- Click **"Deploy"** button
- Wait 2-3 minutes while Vercel builds
- You'll see a success screen with confetti! 🎉

### 7. Get Your URL

Your frontend will be live at:
```
https://tor-unveil.vercel.app
```
(or similar - Vercel will show you the exact URL)

---

## ✅ Step 3: Update Backend CORS

Now that you have your Vercel URL, update the backend:

**Edit `backend/src/api/main.py`:**

Find the CORS section (around line 30-40) and update:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://tor-unveil.vercel.app",  # Your Vercel URL
        "https://*.vercel.app"  # All Vercel preview URLs
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Commit and push:**
```bash
git add backend/src/api/main.py
git commit -m "Add Vercel URL to CORS"
git push origin main
```

Render will auto-redeploy the backend!

---

## 🧪 Step 4: Test Your Deployed App

### 1. Open Your Frontend
Visit: `https://tor-unveil.vercel.app` (your actual URL)

### 2. Check Dashboard
- Should load without errors
- Stats should show (even if zeros)

### 3. Open Browser DevTools
- Press F12
- Go to **Console** tab
- Should see NO CORS errors

### 4. Test Upload
- Go to Upload page
- Upload your sample PCAP (`backend/data/sample.pcap`)
- Click "Analyze"
- Check results!

---

## 🎯 Your Live URLs

**Frontend:** `https://tor-unveil.vercel.app`
**Backend API:** `https://tor-unveil-dil6.onrender.com`
**API Docs:** `https://tor-unveil-dil6.onrender.com/docs`

---

## 🔄 Future Updates

Whenever you make changes:

```bash
git add .
git commit -m "Your changes"
git push origin main
```

**Both Vercel and Render will auto-deploy!** 🚀

---

## 🐛 Troubleshooting

### Build fails on Vercel?
- Check that Root Directory is set to `frontend`
- Verify `package.json` exists in `frontend/`
- Check build logs for specific errors

### Frontend can't connect to backend?
- Verify `VITE_API_URL` environment variable
- Check CORS settings in backend
- Open browser console for error messages

### "Module not found" errors?
- Make sure all dependencies are in `frontend/package.json`
- Try redeploying

---

## 💡 Pro Tips

1. **Custom Domain**: You can add a custom domain in Vercel settings
2. **Preview Deployments**: Every PR gets a preview URL automatically
3. **Analytics**: Enable Vercel Analytics for free
4. **Logs**: Check deployment logs in Vercel dashboard

---

**Just go to vercel.com and import your GitHub repo - it's that easy!** 🎉
