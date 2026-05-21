#!/bin/bash
# WiFi Analyser — Quick Launch Script
# Usage: bash run.sh

echo "=============================================="
echo "  📡 WiFi Analyser — Setup & Launch"
echo "=============================================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip3 install -r requirements.txt --quiet

echo ""
echo "🚀 Starting WiFi Analyser..."
echo "   Open your browser: http://localhost:5000"
echo "   Press Ctrl+C to stop"
echo "=============================================="

# Run with sudo for ARP scanning (required on Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "⚠️  Running with sudo (needed for ARP scanning on Linux)"
    sudo python3 app.py
else
    python3 app.py
fi
