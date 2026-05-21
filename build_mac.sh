#!/bin/bash
# ─────────────────────────────────────────────────────────
#  WiFi Analyser — macOS .app Builder
#  Run this once on your Mac to create the .app bundle
#  Usage: bash build_mac.sh
# ─────────────────────────────────────────────────────────

set -e   # Stop on any error

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   📡 WiFi Analyser — macOS App Builder   ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── Check Python ───────────────────────────────
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Install from https://python.org"
    exit 1
fi

PYTHON=$(which python3)
echo "✅ Python: $($PYTHON --version)"

# ── Install dependencies ───────────────────────
echo ""
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt --quiet
pip3 install pyinstaller --quiet
echo "✅ Dependencies installed"

# ── Clean previous builds ──────────────────────
echo ""
echo "🧹 Cleaning previous builds..."
rm -rf build dist
echo "✅ Cleaned"

# ── Build .app ────────────────────────────────
echo ""
echo "🔨 Building macOS .app bundle..."
echo "   (This takes 1-3 minutes...)"
echo ""
pyinstaller wifi_analyser.spec --noconfirm

# ── Check result ───────────────────────────────
if [ -d "dist/WiFi Analyser.app" ]; then
    echo ""
    echo "╔══════════════════════════════════════════╗"
    echo "║   ✅ BUILD SUCCESSFUL!                   ║"
    echo "╠══════════════════════════════════════════╣"
    echo "║   📁 Location:                           ║"
    echo "║   dist/WiFi Analyser.app                 ║"
    echo "║                                          ║"
    echo "║   To run:                                ║"
    echo "║   Double-click WiFi Analyser.app         ║"
    echo "║   (or drag to Applications folder)       ║"
    echo "║                                          ║"
    echo "║   ⚠️  First launch: right-click → Open   ║"
    echo "║   (bypasses Gatekeeper on first run)     ║"
    echo "╚══════════════════════════════════════════╝"
    echo ""

    # Open the dist folder in Finder
    open dist/
else
    echo "❌ Build failed. Check the output above for errors."
    exit 1
fi
