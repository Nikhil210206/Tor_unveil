# 🔍 TOR Network Analysis Tool

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

## 📁 Project Structure

```
Tor_unveil/
├── src/
│   ├── collector/
│   │   └── pcap_ingest.py          # PCAP ingestion and flow extraction
│   ├── parser/
│   │   └── tor_extractor.py        # TOR traffic detection
│   ├── correlator/
│   │   └── correlation_engine.py   # Flow correlation analysis
│   ├── scorer/
│   │   └── confidence.py           # Confidence scoring
│   ├── db/
│   │   └── models.py               # SQLAlchemy database models
│   ├── web/
│   │   └── app.py                  # Streamlit dashboard
│   ├── report/
│   │   └── generator.py            # PDF report generation
│   └── utils/
│       └── logger.py               # Structured logging
├── data/
│   ├── tor_node_list.json          # TOR relay database
│   └── sample.pcap                 # Sample PCAP (user-provided)
├── scripts/
│   ├── setup_env.sh                # Environment setup
│   ├── run_demo.sh                 # Demo pipeline
│   └── ingest_sample.py            # Python demo script
├── tests/
│   ├── test_pcap_ingest.py         # PCAP ingestion tests
│   └── test_confidence.py          # Scoring tests
├── reports/                        # Generated PDF reports
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## 🔧 Usage

### Command-Line Interface

#### Ingest PCAP
```bash
python -m src.collector.pcap_ingest \
  --file data/capture.pcap \
  --db tor_analysis.db \
  --batch-size 1000
```

#### Analyze TOR Indicators
```bash
python -m src.parser.tor_extractor \
  --analyze \
  --db tor_analysis.db
```

#### Correlate Flows
```bash
python -m src.correlator.correlation_engine \
  --db tor_analysis.db \
  --time-window 10 \
  --min-weight 0.3
```

#### Score Flows
```bash
python -m src.scorer.confidence \
  --db tor_analysis.db
```

#### Generate Report
```bash
python -m src.report.generator \
  --db tor_analysis.db \
  --output reports/forensic_report.pdf \
  --title "TOR Analysis Report"
```

### Python API

```python
from pathlib import Path
from src.db.models import init_database
from src.collector.pcap_ingest import PcapIngestor
from src.parser.tor_extractor import TorExtractor
from src.correlator.correlation_engine import CorrelationEngine
from src.scorer.confidence import ConfidenceScorer

# Initialize database
db_manager = init_database(Path("tor_analysis.db"))

# Ingest PCAP
ingestor = PcapIngestor(db_manager)
flow_count = ingestor.ingest_pcap(Path("data/sample.pcap"))

# Load TOR nodes and analyze
extractor = TorExtractor(db_manager)
extractor.load_tor_nodes_from_file(Path("data/tor_node_list.json"))
tor_flows = extractor.analyze_flows()

# Correlate flows
correlator = CorrelationEngine(db_manager)
correlations = correlator.correlate_flows()

# Score flows
scorer = ConfidenceScorer(db_manager)
scorer.score_all_flows()
high_conf = scorer.get_high_confidence_flows(min_score=60.0)

print(f"Found {len(high_conf)} high-confidence TOR flows")
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test
pytest tests/test_pcap_ingest.py -v
```

## 📊 Dashboard Features

### Overview Page
- Summary metrics (total flows, suspects, critical alerts)
- Confidence score distribution histogram
- Category breakdown pie chart
- Top suspect flows table

### Data Ingestion
- Upload PCAP files
- Load TOR node lists
- Download latest TOR consensus
- Automated analysis pipeline

### Flow Analysis
- Advanced filtering (score, category, protocol)
- Detailed flow inspection
- Payload hex viewer
- Correlation viewer

### Network Graph
- Interactive correlation graph
- Color-coded by confidence
- Node/edge weights
- Zoom and pan controls

### Timeline
- Flow activity over time
- Confidence score trends
- Hourly aggregation

### Reports
- Generate PDF forensic reports
- View previous reports
- Download reports

## 🔍 Detection Heuristics

### TOR Node Matching
- Matches destination IPs against known TOR relay database
- Identifies Guard, Exit, and Middle relays
- Detects directory authority connections (port 9030)

### Pattern Detection
- **TLS Handshake**: Identifies TLS client hello patterns
- **TOR Handshake**: Detects TOR-specific cell structures
- **Obfsproxy**: High-entropy payload analysis for obfuscated traffic
- **Port Analysis**: Common TOR ports (9001, 9030, 9050, 9051, 9150)

### Correlation Algorithm
1. **Timing Window**: Correlates flows within configurable time window (default: 10s)
2. **Entry/Exit Pattern**: Identifies Guard → Exit flow pairs
3. **Packet Similarity**: Compares packet sizes and counts
4. **Source Analysis**: Groups flows by internal source IPs

### Confidence Scoring
- **TOR Node Match** (40 points): Direct relay IP/port match
- **Timing Correlation** (30 points): Strong temporal relationships
- **Payload Similarity** (20 points): TLS/obfsproxy patterns
- **Unusual Patterns** (10 points): Suspicious ports, long connections

## 🗄️ Database Schema

### Tables
- **flows**: Network flow records with TOR indicators
- **tor_nodes**: Known TOR relay information
- **correlations**: Flow correlation relationships
- **alerts**: Security alerts for suspicious activity
- **reports**: Generated report metadata

### Configuration

For PostgreSQL (production):
```python
db_manager = DatabaseManager(
    "postgresql://user:password@localhost:5432/tor_analysis"
)
```

For SQLite (development/demo):
```python
db_manager = DatabaseManager("sqlite:///tor_analysis.db")
```

## 📦 Sample Data

### Getting Sample PCAPs
1. **Wireshark Sample Captures**: https://wiki.wireshark.org/SampleCaptures
2. **NETRESEC**: https://www.netresec.com/?page=PcapFiles
3. **Malware Traffic Analysis**: https://www.malware-traffic-analysis.net/

### TOR Node List
The tool can download the latest TOR consensus automatically:
```bash
python -m src.parser.tor_extractor --download
```

Or use the provided sample: `data/tor_node_list.json`

## 🛠️ Configuration

### Environment Variables
Create a `.env` file:
```bash
DATABASE_URL=sqlite:///tor_analysis.db
LOG_LEVEL=INFO
TIME_WINDOW_SECONDS=10
MIN_CORRELATION_WEIGHT=0.3
```

### Logging
Logs are written to:
- Console (INFO level)
- `logs/` directory (JSON format)

## 🚧 Troubleshooting

### Common Issues

**1. Scapy Permission Errors**
```bash
# Run with sudo or adjust capabilities
sudo setcap cap_net_raw,cap_net_admin=eip $(which python3)
```

**2. Large PCAP Files**
- Use streaming mode (enabled by default)
- Increase batch size for better performance
- Consider splitting large files

**3. Missing TOR Nodes**
```bash
# Re-download TOR consensus
python -m src.parser.tor_extractor --download
```

**4. Dashboard Not Loading**
```bash
# Check Streamlit is installed
pip install streamlit --upgrade

# Clear cache
streamlit cache clear
```

## 🔮 Future Enhancements

- [ ] Real-time packet capture integration.
- [ ] Machine learning-based classification.
- [ ] GeoIP visualization.
- [ ] YARA rule integration.
- [ ] Elasticsearch backend support.
- [ ] REST API for integration.
- [ ] Docker containerization.
- [ ] Multi-threaded processing.

## 📚 References

- [TOR Project](https://www.torproject.org/)
- [TOR Protocol Specification](https://spec.torproject.org/)
- [Scapy Documentation](https://scapy.readthedocs.io/)
- [Stem Library](https://stem.torproject.org/)

## 👥 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- TOR Project for relay data
- Scapy team for packet processing
- Streamlit for the dashboard framework
- The security research community

## 📧 Contact

For questions, issues, or collaboration:
- Open an issue on GitHub
- Email: security@example.com

---

**Remember**: Use this tool responsibly and ethically. Always obtain proper authorization before analyzing the network traffic.
