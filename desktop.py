import sys
import subprocess
import time
import requests
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl


FLASK_URL = "http://127.0.0.1:5000/"


# --------------------------
# Start Flask Server (One-Time)
# --------------------------

def start_flask_once():
    """Start Flask ONLY if not already running."""
    try:
        requests.get(FLASK_URL, timeout=1)
        print("Flask already running.")
        return
    except:
        pass

    print("Starting Flask server...")
    subprocess.Popen(
        [sys.executable, "app.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


# --------------------------
# Wait for Flask Server Ready
# --------------------------

def wait_for_flask():
    """Wait up to 10 seconds for Flask to come online."""
    for i in range(40):  # 40 × 0.25s = 10 seconds
        try:
            r = requests.get(FLASK_URL)
            if r.status_code == 200:
                print("Flask is online.")
                return True
        except:
            pass
        time.sleep(0.25)
    print("❌ Flask server failed to start.")
    return False


# --------------------------
# Launch UI Window
# --------------------------

def launch_ui():
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("Triptide")
    window.resize(1200, 800)

    webview = QWebEngineView()
    webview.load(QUrl(FLASK_URL))

    window.setCentralWidget(webview)
    window.show()

    sys.exit(app.exec_())


# --------------------------
# MAIN
# --------------------------

if __name__ == "__main__":
    start_flask_once()
    if wait_for_flask():
        launch_ui()
