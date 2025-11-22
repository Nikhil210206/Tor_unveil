# 🚀 Quick Start Guide - Monorepo Setup

## ✅ Setup Complete!

Your project is now organized as a monorepo:

```
Tor_unveil/
├── backend/          # All Python code is here
│   ├── src/
│   ├── tests/
│   ├── data/
│   └── requirements.txt
├── frontend/         # Add Lovable AI code here
└── README.md
```

## 🔧 Running the Backend

### From the root directory:
```bash
cd /Users/nikhil/Documents/Tor_unveil
cd backend
source ../venv/bin/activate
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Or use this one-liner:
```bash
cd /Users/nikhil/Documents/Tor_unveil && cd backend && source ../venv/bin/activate && uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**Backend will be available at:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

## 📱 Adding the Frontend

1. **Download code from Lovable AI**
   - Click "Download Code" or "Export"
   - Extract the zip file

2. **Copy to frontend directory**
   ```bash
   cd /Users/nikhil/Documents/Tor_unveil
   # Copy all Lovable AI files into frontend/
   cp -r /path/to/lovable-code/* frontend/
   ```

3. **Install and run**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

**Frontend will be available at:** http://localhost:5173

## 🔗 Connecting Frontend to Backend

The frontend should already be configured to call `http://localhost:8000` for the API.

If you need to change it, look for a file like:
- `frontend/src/config.ts`
- `frontend/src/lib/api.ts`
- Or search for `localhost:8000` in the frontend code

## 🚀 Deployment

### Backend → Railway
```bash
cd /Users/nikhil/Documents/Tor_unveil
# Railway will use the railway.toml config
railway login
railway init
railway up
```

### Frontend → Vercel
```bash
cd /Users/nikhil/Documents/Tor_unveil/frontend
vercel
```

Or connect your GitHub repo to Vercel for automatic deployments.

## 📊 Current Status

✅ Backend API running at http://localhost:8000
✅ Monorepo structure set up
✅ Deployment configs created
⏳ Waiting for frontend code from Lovable AI

## 🎯 Next Steps

1. ✅ Backend is running
2. Add Lovable AI frontend code to `frontend/`
3. Run `cd frontend && npm install && npm run dev`
4. Test the full stack locally
5. Deploy both to production

## 💡 Pro Tips

- **Keep backend running** in one terminal
- **Run frontend** in another terminal
- **Check API docs** at http://localhost:8000/docs
- **Test endpoints** before connecting frontend

---

**Everything is ready! Just add your frontend code and you're good to go!** 🎉
