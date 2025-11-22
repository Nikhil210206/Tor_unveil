# 🔍 TOR Network Analysis Tool

<<<<<<< HEAD
Full-stack application for analyzing network traffic and detecting TOR (The Onion Router) usage patterns.
=======
A comprehensive Python-based tool for analyzing network traffic to detect and correlate TOR (The Onion Router) usage patterns. This tool ingests PCAP files, identifies TOR-related indicators, correlates flows to detect potential TOR circuits, computes confidence scores, and provides an interactive Streamlit dashboard with network visualizations and automated PDF forensic reports.

![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ⚠️ Legal & Ethical Notice

**IMPORTANT**: This tool is designed for legitimate security research, network forensics, and authorized penetration testing only. Users must:

- Obtain proper authorization before analyzing any network traffic.
- Comply with all applicable laws and regulations (GDPR, CFAA, etc.)
- Anonymize data when sharing or publishing results.
- Respect privacy and ethical guidelines.

**Unauthorized network monitoring may be illegal in your jurisdiction.**

## 🎯 Features

### Core Capabilities
- **PCAP Ingestion**: Stream large PCAP files efficiently using Scapy
- **TOR Detection**: Identify TOR traffic using multiple heuristics:
  - Known TOR relay IP/port matching.
  - TLS handshake pattern detection.
  - Obfsproxy/pluggable transport identification.
  - Directory fetch detection.
- **Flow Correlation**: Advanced timing and pattern analysis to identify entry/exit node pairs
- **Confidence Scoring**: Multi-factor scoring system (0-100) with categories:
  - Low (0-30)
  - Medium (30-60)
  - High (60-85)
  - Critical (85-100)
- **Interactive Dashboard**: Streamlit-based UI with:
  - Real-time statistics
  - Network graph visualization (NetworkX + Pyvis)
  - Timeline analysis (Plotly)
  - Flow detail inspection
  - Filterable data tables
- **Forensic Reports**: Auto-generated PDF reports with:
  - Executive summary
  - Statistical analysis
  - High-confidence flow tables
  - Correlation evidence
  - Actionable recommendations

## 📋 Requirements

- Python 3.11 or higher
- 4GB+ RAM (for processing large PCAPs)
- SQLite (included) or PostgreSQL (optional)
- Modern web browser (for dashboard)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
cd /path/to/Tor_unveil

# Run setup script
chmod +x scripts/setup_env.sh
./scripts/setup_env.sh

# Activate virtual environment
source venv/bin/activate
```

### 2. Download TOR Node List

```bash
# Download latest TOR consensus
python -m src.parser.tor_extractor --download --output data/tor_node_list.json
```

### 3. Run Analysis on Sample Data

```bash
# Option A: Use the demo script (requires sample.pcap in data/)
chmod +x scripts/run_demo.sh
./scripts/run_demo.sh

# Option B: Use the Python demo script
python scripts/ingest_sample.py --pcap data/sample.pcap
```

### 4. Launch Dashboard

```bash
streamlit run src/web/app.py
```

The dashboard will open at `http://localhost:8501`
>>>>>>> a34f650c0b120d2793d0bb40f9bbd218e8cc1a89

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

<<<<<<< HEAD
This tool is designed for legitimate security research, network forensics, and authorized penetration testing only. Users must:
=======
- [ ] Real-time packet capture integration.
- [ ] Machine learning-based classification.
- [ ] GeoIP visualization.
- [ ] YARA rule integration.
- [ ] Elasticsearch backend support.
- [ ] REST API for integration.
- [ ] Docker containerization.
- [ ] Multi-threaded processing.
>>>>>>> a34f650c0b120d2793d0bb40f9bbd218e8cc1a89

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

<<<<<<< HEAD
**Built for security research and network forensics** 🔍
=======
**Remember**: Use this tool responsibly and ethically. Always obtain proper authorization before analyzing the network traffic.
>>>>>>> a34f650c0b120d2793d0bb40f9bbd218e8cc1a89
