# 🚀 Frontend Deployment - Vercel vs Netlify

## ✅ Backend Deployed!
Your backend is live at: `https://tor-analysis-backend.onrender.com`

Now let's deploy the frontend. **Choose one:**

---

## 🟢 Option 1: Vercel (Recommended - Easiest)

### Why Vercel?
- ✅ Built for React/Vite
- ✅ Fastest deployment
- ✅ Best performance
- ✅ Auto-preview deployments

### Quick Deploy with Vercel CLI

```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Login
vercel login

# 3. Deploy
cd /Users/nikhil/Documents/Tor_unveil/frontend
vercel --prod
```

**Answer the prompts:**
```
? Set up and deploy? Yes
? Which scope? (Your account)
? Link to existing project? No
? What's your project's name? tor-unveil-frontend
? In which directory is your code located? ./
? Want to override settings? No
```

**Done!** You'll get a URL like: `https://tor-unveil-frontend.vercel.app`

### Set Environment Variable

```bash
vercel env add VITE_API_URL production
```

When prompted, enter:
```
https://tor-analysis-backend.onrender.com
```

Then redeploy:
```bash
vercel --prod
```

---

## 🔵 Option 2: Netlify (Also Great)

### Why Netlify?
- ✅ Great for static sites
- ✅ Easy drag-and-drop
- ✅ Good free tier
- ✅ Simple setup

### Method A: Netlify CLI (Fastest)

```bash
# 1. Install Netlify CLI
npm install -g netlify-cli

# 2. Login
netlify login

# 3. Build your frontend
cd /Users/nikhil/Documents/Tor_unveil/frontend
npm run build

# 4. Deploy
netlify deploy --prod
```

**Answer the prompts:**
```
? Create & configure a new site? Yes
? Team: (Your team)
? Site name: tor-unveil-frontend
? Publish directory: dist
```

### Method B: Netlify Dashboard (Easiest)

1. Go to https://app.netlify.com
2. Click **"Add new site"** → **"Import an existing project"**
3. Connect GitHub
4. Select your `Tor_unveil` repository
5. Configure:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/dist`
6. Add environment variable:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://tor-analysis-backend.onrender.com`
7. Click **"Deploy site"**

**Done!** You'll get a URL like: `https://tor-unveil-frontend.netlify.app`

---

## 🔧 Before Deploying - Update API URL

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

---

## 🔗 Update Backend CORS

**Edit `backend/src/api/main.py`:**

Find the CORS section and update:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://tor-unveil-frontend.vercel.app",  # If using Vercel
        "https://tor-unveil-frontend.netlify.app",  # If using Netlify
        "https://*.vercel.app",  # All Vercel previews
        "https://*.netlify.app"  # All Netlify previews
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Commit and push:**
```bash
git add backend/src/api/main.py
git commit -m "Update CORS for production frontend"
git push origin main
```

Render will auto-redeploy!

---

## 📊 Comparison

| Feature | Vercel | Netlify |
|---------|--------|---------|
| **Speed** | ⚡⚡⚡ Fastest | ⚡⚡ Fast |
| **React/Vite** | ✅ Optimized | ✅ Good |
| **CLI** | ✅ Excellent | ✅ Good |
| **Dashboard** | ✅ Modern | ✅ User-friendly |
| **Free Tier** | ✅ Generous | ✅ Generous |
| **Auto Deploy** | ✅ Yes | ✅ Yes |
| **Preview URLs** | ✅ Yes | ✅ Yes |

**My Recommendation: Vercel** (slightly better for React/Vite)

---

## 🎯 Quick Commands

### Vercel (3 commands):
```bash
npm install -g vercel
vercel login
cd frontend && vercel --prod
```

### Netlify (4 commands):
```bash
npm install -g netlify-cli
netlify login
cd frontend && npm run build
netlify deploy --prod
```

---

## ✅ After Deployment

1. **Test your frontend URL**
2. **Open browser DevTools** (F12) → Console
3. **Check for CORS errors** (should be none)
4. **Upload a PCAP** and test the full flow
5. **Share your live URLs!** 🎉

---

## 🆘 Troubleshooting

### Frontend can't connect to backend?
- Check `VITE_API_URL` environment variable
- Verify CORS settings in backend
- Check browser console for errors

### Build fails?
- Make sure you're in `frontend/` directory
- Run `npm install` first
- Check for TypeScript errors

---

**Choose Vercel or Netlify and deploy!** 🚀

Both are excellent - Vercel is slightly faster for React apps, but Netlify has a great UI. Pick whichever you prefer!
