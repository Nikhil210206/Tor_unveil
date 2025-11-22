#!/bin/bash

# TOR Network Analysis Tool - Setup Script

set -e

echo "🔧 Setting up TOR Network Analysis Tool..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data
mkdir -p reports
mkdir -p logs

# Initialize database
echo "🗄️  Initializing database..."
python3 -c "from src.db.models import init_database; init_database()"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Load TOR nodes: python -m src.parser.tor_extractor --download"
echo "  3. Run the dashboard: streamlit run src/web/app.py"
echo ""
