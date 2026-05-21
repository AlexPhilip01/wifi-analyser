"""
WiFi Analyser — macOS App Launcher
Starts Flask server and opens browser automatically.
"""

import sys
import os
import threading
import webbrowser
import time
import signal

# ── Fix paths when running inside .app bundle ──────────────────────
if getattr(sys, 'frozen', False):
    # Running as PyInstaller bundle
    BASE_DIR = sys._MEIPASS
    APP_DIR  = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    APP_DIR  = BASE_DIR

# Add base dir to path so Flask can find templates/static
sys.path.insert(0, BASE_DIR)
os.chdir(BASE_DIR)

from app import app

PORT = 5001

def open_browser():
    """Wait for Flask to start, then open browser."""
    time.sleep(1.5)
    webbrowser.open(f"http://localhost:{PORT}")

def start_server():
    """Run Flask server."""
    app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False)

if __name__ == "__main__":
    print("📡 WiFi Analyser starting...")
    print(f"   Opening http://localhost:{PORT}")

    # Start browser opener in background
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()

    # Start Flask (blocking)
    start_server()
