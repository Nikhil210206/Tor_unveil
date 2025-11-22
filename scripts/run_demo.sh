#!/bin/bash

# TOR Network Analysis Tool - Demo Script

set -e

echo "🚀 Running TOR Network Analysis Demo..."
echo ""

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not activated. Activating..."
    source venv/bin/activate
fi

# Check if sample PCAP exists
if [ ! -f "data/sample.pcap" ]; then
    echo "⚠️  Sample PCAP not found. Please add a PCAP file to data/sample.pcap"
    echo "   You can download sample PCAPs from:"
    echo "   - https://www.netresec.com/?page=PcapFiles"
    echo "   - https://wiki.wireshark.org/SampleCaptures"
    exit 1
fi

# Check if TOR node list exists
if [ ! -f "data/tor_node_list.json" ]; then
    echo "📥 Downloading TOR consensus..."
    python -m src.parser.tor_extractor --download --output data/tor_node_list.json
fi

echo ""
echo "Step 1: Ingesting PCAP file..."
python -m src.collector.pcap_ingest --file data/sample.pcap --db tor_analysis.db

echo ""
echo "Step 2: Analyzing TOR indicators..."
python -m src.parser.tor_extractor --analyze --db tor_analysis.db

echo ""
echo "Step 3: Correlating flows..."
python -m src.correlator.correlation_engine --db tor_analysis.db

echo ""
echo "Step 4: Scoring flows..."
python -m src.scorer.confidence --db tor_analysis.db

echo ""
echo "Step 5: Generating report..."
python -m src.report.generator --db tor_analysis.db --output reports/demo_report.pdf

echo ""
echo "✅ Demo complete!"
echo ""
echo "📊 Launch the dashboard to explore results:"
echo "   streamlit run src/web/app.py"
echo ""
echo "📄 View the generated report:"
echo "   open reports/demo_report.pdf"
echo ""
