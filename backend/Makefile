.PHONY: help install test clean run dashboard

help:
	@echo "TOR Network Analysis Tool - Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  make install    - Install dependencies and setup environment"
	@echo "  make test       - Run test suite"
	@echo "  make clean      - Clean generated files"
	@echo "  make dashboard  - Launch Streamlit dashboard"
	@echo "  make demo       - Run demo analysis pipeline"

install:
	@echo "Installing dependencies..."
	python3 -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	@echo "✓ Installation complete"

test:
	@echo "Running tests..."
	./venv/bin/pytest tests/ -v --cov=src --cov-report=term-missing

clean:
	@echo "Cleaning generated files..."
	rm -rf __pycache__ .pytest_cache .coverage htmlcov
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -f tor_analysis.db
	@echo "✓ Cleanup complete"

dashboard:
	@echo "Launching Streamlit dashboard..."
	./venv/bin/streamlit run src/web/app.py

demo:
	@echo "Running demo pipeline..."
	chmod +x scripts/run_demo.sh
	./scripts/run_demo.sh

dev:
	@echo "Setting up development environment..."
	chmod +x scripts/setup_env.sh
	./scripts/setup_env.sh
