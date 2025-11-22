# 🚀 TOR Analysis - Backend API Ready!

## ✅ What's Ready

I've created a **complete REST API backend** using FastAPI that exposes all the TOR analysis functionality. You can now build any frontend you want with Lovable AI!

## 📡 API Server

### Start the Server

```bash
cd /Users/nikhil/Documents/Tor_unveil
source venv/bin/activate
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

**API will be available at:** `http://localhost:8000`

**Interactive Docs:** `http://localhost:8000/docs` (Swagger UI)

## 🎯 Key Endpoints for Your Frontend

### 1. Get Statistics
```javascript
GET /api/stats
// Returns: total flows, suspects, critical alerts, etc.
```

### 2. Upload PCAP
```javascript
POST /api/upload
// Form data with file upload
```

### 3. Run Analysis
```javascript
POST /api/analyze
// Body: { time_window: 10, min_correlation_weight: 0.3 }
```

### 4. Get Flows
```javascript
GET /api/flows?min_score=60&limit=50
// Returns: array of flows with confidence scores
```

### 5. Get Graph Data
```javascript
GET /api/graph
// Returns: { nodes: [...], edges: [...] } for visualization
```

### 6. Get Timeline
```javascript
GET /api/timeline
// Returns: array of time-series data
```

### 7. Generate Report
```javascript
POST /api/reports/generate?title=My Report
// Returns: PDF download URL
```

## 💡 Frontend Integration Example

```typescript
// Example for Lovable AI or any React/Next.js app

// 1. Get stats
const stats = await fetch('http://localhost:8000/api/stats')
  .then(res => res.json());

// 2. Upload PCAP
const formData = new FormData();
formData.append('file', pcapFile);
await fetch('http://localhost:8000/api/upload', {
  method: 'POST',
  body: formData
});

// 3. Run analysis
await fetch('http://localhost:8000/api/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ time_window: 10 })
});

// 4. Get results
const flows = await fetch('http://localhost:8000/api/flows?min_score=60')
  .then(res => res.json());

// 5. Get graph for visualization
const graph = await fetch('http://localhost:8000/api/graph')
  .then(res => res.json());
```

## 🎨 What to Build with Lovable AI

### Suggested Pages

1. **Dashboard** - Show stats cards, charts
2. **Upload** - Drag & drop PCAP upload
3. **Flows Table** - Sortable, filterable table
4. **Network Graph** - Interactive D3.js/Cytoscape visualization
5. **Timeline** - Time-series chart (Recharts/Chart.js)
6. **Reports** - List and download PDFs

### UI Components to Create

- Stats cards (total flows, suspects, critical)
- File upload with progress
- Data table with filters
- Network graph visualization
- Timeline chart
- PDF download buttons

## 📚 Full Documentation

See [API_README.md](file:///Users/nikhil/Documents/Tor_unveil/API_README.md) for:
- Complete endpoint documentation
- Request/response examples
- Integration guides for all frameworks
- Production deployment tips

## 🔥 Quick Test

```bash
# Start the API
uvicorn src.api.main:app --reload

# In another terminal, test it:
curl http://localhost:8000/api/stats
```

## ✨ Benefits

- ✅ **Complete Backend** - All analysis logic ready
- ✅ **RESTful API** - Standard HTTP endpoints
- ✅ **Auto Documentation** - Swagger UI included
- ✅ **CORS Enabled** - Works with any frontend
- ✅ **Type Safe** - Pydantic models for validation
- ✅ **Production Ready** - Can deploy with Gunicorn/Docker

## 🎯 Next Steps

1. **Start the API server** (command above)
2. **Open Swagger docs** at http://localhost:8000/docs
3. **Build your frontend** with Lovable AI
4. **Use the endpoints** documented above

The backend is 100% ready for your custom UI! 🚀
