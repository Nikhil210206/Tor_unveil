# ✅ Full Stack Running - Testing Guide

## 🎉 Current Status

Both frontend and backend are running successfully!

- ✅ **Backend API**: http://localhost:8000
- ✅ **Frontend App**: http://localhost:5173 (or check your terminal)
- ✅ **API Docs**: http://localhost:8000/docs
- ✅ **Connection**: Frontend configured to call backend at `http://localhost:8000`

## 🧪 Testing Checklist

### 1. Test Backend API (http://localhost:8000/docs)

Open http://localhost:8000/docs in your browser and test these endpoints:

- [ ] **GET /api/stats** - Should return statistics (even if all zeros initially)
- [ ] **GET /api/flows** - Should return empty array or existing flows
- [ ] **GET /api/graph** - Should return graph data
- [ ] **GET /api/timeline** - Should return timeline data

### 2. Test Frontend (http://localhost:5173)

Open your frontend URL and check:

- [ ] **Dashboard loads** - Shows stat cards (may be zero)
- [ ] **Navigation works** - Can click between pages
- [ ] **No console errors** - Check browser DevTools (F12)
- [ ] **API calls work** - Check Network tab for successful requests

### 3. Test Upload & Analysis Flow

This is the main workflow:

1. **Go to Upload page** in frontend
2. **Upload a PCAP file** (.pcap or .pcapng)
   - If you don't have one, download: https://wiki.wireshark.org/SampleCaptures
   - Try: http.cap or any small capture file
3. **Configure analysis**:
   - Time window: 10 seconds
   - Min correlation: 0.3
4. **Click "Upload & Analyze"**
5. **Wait for completion**
6. **Check Dashboard** - Should show updated stats
7. **View Flows** - Should show detected flows
8. **Check Graph** - Should show network visualization
9. **Generate Report** - Should create PDF

### 4. Check CORS (Important!)

If you see CORS errors in browser console:

**Backend fix** (`backend/src/api/main.py`):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

The backend should already have `allow_origins=["*"]` which allows all origins for development.

## 🐛 Troubleshooting

### Frontend can't connect to backend

**Check:**
1. Backend is running on port 8000
2. Frontend API config is `http://localhost:8000` (check `frontend/src/lib/api.ts`)
3. No CORS errors in browser console
4. Both servers are running

**Test backend directly:**
```bash
curl http://localhost:8000/api/stats
```

Should return JSON like:
```json
{
  "total_flows": 0,
  "suspect_flows": 0,
  "critical_flows": 0,
  "high_flows": 0,
  "total_correlations": 0,
  "total_tor_nodes": 10
}
```

### Upload fails

**Check:**
1. File is .pcap or .pcapng format
2. File size is reasonable (< 100MB for testing)
3. Backend has write permissions for database
4. Check backend terminal for error messages

### No data showing

**Reason:** You need to upload and analyze a PCAP file first!

The database starts empty. After uploading a PCAP:
- Dashboard will show flow counts
- Flows page will list detected flows
- Graph will show correlations
- Timeline will show activity

## 📊 Sample Data

### Get a test PCAP file:

```bash
# Download a sample
cd /Users/nikhil/Documents/Tor_unveil/backend/data
wget https://wiki.wireshark.org/SampleCaptures?action=AttachFile&do=get&target=http.cap -O sample.pcap
```

Or use any network capture you have.

### Load TOR nodes (optional):

The backend already has sample TOR nodes in `backend/data/tor_node_list.json`.

To download latest:
```bash
cd /Users/nikhil/Documents/Tor_unveil/backend
source ../venv/bin/activate
python -m src.parser.tor_extractor --download --output data/tor_node_list.json
```

## 🎯 Expected Behavior

### After uploading a PCAP:

1. **Dashboard** shows:
   - Total flows: X
   - Suspect flows: Y (flows with score ≥ 30)
   - High/Critical: Based on confidence scores

2. **Flows page** shows:
   - Table of all flows
   - Confidence scores and categories
   - Filter and search options

3. **Graph page** shows:
   - Network visualization
   - Nodes colored by confidence
   - Edges showing correlations

4. **Timeline** shows:
   - Flows plotted over time
   - Confidence scores on Y-axis

5. **Reports** allows:
   - Generate PDF report
   - Download previous reports

## ✨ Demo Flow

**Perfect demo for a hackathon:**

1. Open frontend
2. Show empty dashboard
3. Go to Upload page
4. Upload a PCAP file
5. Watch analysis progress
6. Return to Dashboard - show updated stats
7. Browse Flows - show detected traffic
8. View Graph - show network visualization
9. Generate Report - download PDF
10. 🎉 Success!

## 🚀 Deployment Ready

Once everything works locally:

1. **Push to GitHub**
   ```bash
   cd /Users/nikhil/Documents/Tor_unveil
   git add .
   git commit -m "Complete TOR analysis tool with frontend and backend"
   git push
   ```

2. **Deploy Backend to Railway**
   ```bash
   cd backend
   railway login
   railway init
   railway up
   ```

3. **Deploy Frontend to Vercel**
   - Connect GitHub repo to Vercel
   - Set root directory to `frontend`
   - Add environment variable: `VITE_API_URL=https://your-backend.railway.app`
   - Deploy!

4. **Update frontend API URL** for production in `frontend/src/lib/api.ts`

---

**Everything is ready! Test it out and enjoy your TOR analysis tool!** 🔍🎉
