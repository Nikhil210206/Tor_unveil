#!/bin/bash

# TOR Network Analysis - Monorepo Setup Script
# This script reorganizes the project into backend/ and frontend/ structure

set -e

echo "🔧 Setting up monorepo structure..."

# Stop any running servers first
echo "⚠️  Please stop your running servers (Ctrl+C) before continuing."
read -p "Press Enter when ready to continue..."

cd /Users/nikhil/Documents/Tor_unveil

# Create backend directory
echo "📁 Creating backend directory..."
mkdir -p backend

# Move backend files
echo "📦 Moving backend files..."
mv src backend/ 2>/dev/null || true
mv tests backend/ 2>/dev/null || true
mv scripts backend/ 2>/dev/null || true
mv data backend/ 2>/dev/null || true
mv requirements.txt backend/ 2>/dev/null || true
mv requirements-api.txt backend/ 2>/dev/null || true
mv Makefile backend/ 2>/dev/null || true
mv tor_analysis.db backend/ 2>/dev/null || true

# Move documentation to backend
echo "📄 Moving backend docs..."
mv API_README.md backend/ 2>/dev/null || true
mv BACKEND_READY.md backend/ 2>/dev/null || true

# Keep these in root
echo "📋 Keeping root files..."
# .git, .gitignore, README.md stay in root

# Create placeholder for frontend
echo "📱 Creating frontend placeholder..."
mkdir -p frontend
cat > frontend/README.md << 'EOF'
# Frontend

The React frontend will go here.

## Setup

After adding the Lovable AI generated code:

```bash
npm install
npm run dev
```

The app will run on http://localhost:5173
EOF

# Create new root README
echo "📝 Creating main README..."
cat > README.md << 'EOF'
# 🔍 TOR Network Analysis Tool

Full-stack application for analyzing network traffic and detecting TOR (The Onion Router) usage patterns.

## 📁 Project Structure

```
Tor_unveil/
├── backend/          # Python FastAPI backend
│   ├── src/         # Core analysis modules
│   ├── tests/       # Unit tests
│   ├── data/        # Sample data
│   └── scripts/     # Utility scripts
│
├── frontend/         # React TypeScript frontend (add Lovable AI code here)
│   └── src/         # React components
│
└── README.md        # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt -r requirements-api.txt
```

### Run Backend API

```bash
cd backend
source venv/bin/activate
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## 📚 Documentation

- **Backend API**: See [backend/API_README.md](backend/API_README.md)
- **Frontend Setup**: See [frontend/README.md](frontend/README.md)
- **Lovable AI Prompt**: See [LOVABLE_AI_PROMPT.md](LOVABLE_AI_PROMPT.md)

## 🎯 Features

### Backend (Python/FastAPI)
- ✅ PCAP file ingestion with Scapy
- ✅ TOR traffic detection using multiple heuristics
- ✅ Flow correlation engine with timing analysis
- ✅ Confidence scoring system (0-100)
- ✅ PDF forensic report generation
- ✅ REST API with 15+ endpoints

### Frontend (React/TypeScript)
- ✅ Modern dark theme dashboard
- ✅ Interactive network graph visualization
- ✅ Real-time charts and statistics
- ✅ PCAP file upload with drag & drop
- ✅ Advanced flow filtering and search
- ✅ PDF report generation and download

## 🔧 Development

### Backend
```bash
# Run tests
cd backend
pytest tests/ -v

# Run with auto-reload
uvicorn src.api.main:app --reload
```

### Frontend
```bash
# Development mode
cd frontend
npm run dev

# Build for production
npm run build
```

## 🚀 Deployment

### Backend → Railway
```bash
cd backend
railway login
railway init
railway up
```

### Frontend → Vercel
```bash
cd frontend
vercel
```

Or use the Vercel GitHub integration for automatic deployments.

## 📊 API Endpoints

- `GET /api/stats` - Get overall statistics
- `POST /api/upload` - Upload PCAP file
- `POST /api/analyze` - Run TOR analysis
- `GET /api/flows` - List flows with filtering
- `GET /api/graph` - Get network graph data
- `GET /api/timeline` - Get timeline data
- `POST /api/reports/generate` - Generate PDF report

See full API documentation at `http://localhost:8000/docs`

## ⚠️ Legal Notice

This tool is designed for legitimate security research, network forensics, and authorized penetration testing only. Users must:

- Obtain proper authorization before analyzing any network traffic
- Comply with all applicable laws and regulations
- Anonymize data when sharing or publishing results
- Respect privacy and ethical guidelines

**Unauthorized network monitoring may be illegal in your jurisdiction.**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- TOR Project for relay data
- Scapy team for packet processing
- FastAPI and React communities

---

**Built for security research and network forensics** 🔍
EOF

# Update .gitignore
echo "🔒 Updating .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
venv/
ENV/
env/

# Database
*.db
*.sqlite3

# Logs
*.log
logs/

# Reports
reports/*.pdf

# PCAP files
*.pcap
*.pcapng
data/sample*.pcap

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Frontend
frontend/node_modules/
frontend/dist/
frontend/build/
frontend/.next/
frontend/.cache/
frontend/.env.local
frontend/.env.production.local

# Testing
.pytest_cache/
.coverage
htmlcov/

# Misc
.env
*.bak
EOF

# Create deployment configs
echo "🚢 Creating deployment configs..."

# Railway config for backend
cat > railway.toml << 'EOF'
[build]
builder = "NIXPACKS"
buildCommand = "cd backend && pip install -r requirements.txt -r requirements-api.txt"

[deploy]
startCommand = "cd backend && uvicorn src.api.main:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
EOF

# Vercel config for frontend
mkdir -p frontend
cat > vercel.json << 'EOF'
{
  "buildCommand": "cd frontend && npm run build",
  "outputDirectory": "frontend/dist",
  "devCommand": "cd frontend && npm run dev",
  "installCommand": "cd frontend && npm install"
}
EOF

echo ""
echo "✅ Monorepo setup complete!"
echo ""
echo "📁 New structure:"
echo "   Tor_unveil/"
echo "   ├── backend/      (all Python code)"
echo "   ├── frontend/     (add Lovable AI code here)"
echo "   └── README.md     (main documentation)"
echo ""
echo "🎯 Next steps:"
echo "   1. Add your Lovable AI frontend code to frontend/"
echo "   2. Update API URL in frontend to http://localhost:8000"
echo "   3. Test: cd backend && uvicorn src.api.main:app --reload"
echo "   4. Test: cd frontend && npm run dev"
echo ""
echo "🚀 Ready to rock!"
