# TOR Network Analysis API

REST API backend for the TOR Network Analysis Tool. This API provides all the core functionality via HTTP endpoints, making it easy to integrate with any frontend framework.

## Quick Start

### 1. Install Dependencies

```bash
cd /Users/nikhil/Documents/Tor_unveil
source venv/bin/activate
pip install -r requirements-api.txt
```

### 2. Start the API Server

```bash
# Development mode with auto-reload
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at: `http://localhost:8000`

### 3. View API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## API Endpoints

### General

- `GET /` - API information and endpoint list
- `GET /api/stats` - Get overall statistics

### Flows

- `GET /api/flows` - List flows with filtering
  - Query params: `min_score`, `category`, `limit`, `offset`
- `GET /api/flows/{flow_id}` - Get flow details with correlations

### Data Ingestion

- `POST /api/upload` - Upload PCAP file
  - Form data: `file` (multipart/form-data)
- `POST /api/analyze` - Run complete analysis pipeline
  - Body: `{"time_window": 10, "min_correlation_weight": 0.3}`

### Correlations & Visualization

- `GET /api/correlations` - List correlations
- `GET /api/graph` - Get graph data (nodes & edges)
- `GET /api/timeline` - Get timeline data

### Reports

- `POST /api/reports/generate` - Generate PDF report
  - Query param: `title`
- `GET /api/reports/download/{filename}` - Download report
- `GET /api/reports` - List all reports

### Database

- `DELETE /api/database/reset` - Reset database (dev only)

## Example Usage

### JavaScript/TypeScript

```typescript
// Get statistics
const stats = await fetch('http://localhost:8000/api/stats')
  .then(res => res.json());

// Upload PCAP
const formData = new FormData();
formData.append('file', pcapFile);
const upload = await fetch('http://localhost:8000/api/upload', {
  method: 'POST',
  body: formData
}).then(res => res.json());

// Run analysis
const analysis = await fetch('http://localhost:8000/api/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    time_window: 10,
    min_correlation_weight: 0.3
  })
}).then(res => res.json());

// Get flows
const flows = await fetch('http://localhost:8000/api/flows?min_score=60&limit=50')
  .then(res => res.json());

// Get graph data
const graph = await fetch('http://localhost:8000/api/graph')
  .then(res => res.json());
```

### Python

```python
import requests

# Get statistics
stats = requests.get('http://localhost:8000/api/stats').json()

# Upload PCAP
with open('sample.pcap', 'rb') as f:
    files = {'file': f}
    upload = requests.post('http://localhost:8000/api/upload', files=files).json()

# Run analysis
analysis = requests.post('http://localhost:8000/api/analyze', json={
    'time_window': 10,
    'min_correlation_weight': 0.3
}).json()

# Get flows
flows = requests.get('http://localhost:8000/api/flows', params={
    'min_score': 60,
    'limit': 50
}).json()
```

### cURL

```bash
# Get statistics
curl http://localhost:8000/api/stats

# Upload PCAP
curl -X POST -F "file=@sample.pcap" http://localhost:8000/api/upload

# Run analysis
curl -X POST -H "Content-Type: application/json" \
  -d '{"time_window": 10, "min_correlation_weight": 0.3}' \
  http://localhost:8000/api/analyze

# Get flows
curl "http://localhost:8000/api/flows?min_score=60&limit=50"

# Generate report
curl -X POST "http://localhost:8000/api/reports/generate?title=My%20Report"
```

## Response Models

### StatsResponse
```json
{
  "total_flows": 1234,
  "suspect_flows": 56,
  "critical_flows": 12,
  "high_flows": 23,
  "total_correlations": 89,
  "total_tor_nodes": 10
}
```

### FlowResponse
```json
{
  "id": 1,
  "src_ip": "192.168.1.100",
  "src_port": 50000,
  "dst_ip": "185.220.101.1",
  "dst_port": 9001,
  "protocol": "TCP",
  "ts_start": "2025-11-22T19:00:00",
  "pkt_count": 100,
  "byte_count": 10000,
  "confidence_score": 85.5,
  "confidence_category": "Critical",
  "possible_tor_handshake": true,
  "relay_comm": true,
  "directory_fetch": false,
  "obfsproxy_candidate": false
}
```

### Graph Data
```json
{
  "nodes": [
    {
      "id": 1,
      "label": "192.168.1.100→185.220.101.1",
      "score": 85.5,
      "category": "Critical"
    }
  ],
  "edges": [
    {
      "source": 1,
      "target": 2,
      "weight": 0.75,
      "type": "entry_exit"
    }
  ]
}
```

## CORS Configuration

The API is configured to allow all origins by default for development. For production, update the CORS settings in `src/api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Frontend Integration

This API is designed to work with any frontend framework:

- **React/Next.js**: Use `fetch` or `axios`
- **Vue/Nuxt**: Use `$fetch` or `axios`
- **Angular**: Use `HttpClient`
- **Svelte/SvelteKit**: Use `fetch`
- **Lovable AI**: Perfect for rapid UI development!

## Development

### Run with Auto-Reload
```bash
uvicorn src.api.main:app --reload
```

### Test Endpoints
```bash
# Install httpie (optional)
pip install httpie

# Test endpoints
http GET localhost:8000/api/stats
http POST localhost:8000/api/analyze time_window:=10
```

## Production Deployment

### Using Gunicorn + Uvicorn Workers
```bash
pip install gunicorn
gunicorn src.api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt requirements-api.txt ./
RUN pip install -r requirements.txt -r requirements-api.txt

COPY . .
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Security Notes

- Enable authentication for production
- Configure proper CORS origins
- Use HTTPS in production
- Rate limit endpoints
- Validate file uploads
- Sanitize user inputs

## Next Steps

1. **Start the API**: `uvicorn src.api.main:app --reload`
2. **Test with Swagger**: Visit http://localhost:8000/docs
3. **Build your frontend**: Use Lovable AI or any framework
4. **Integrate**: Use the endpoints documented above

The backend is ready for your custom frontend! 🚀
