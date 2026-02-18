import threading
import subprocess
import sys
import os
import time


def start_flask():
    """Runs Flask in a non-blocking thread."""
    env = os.environ.copy()

    # Allow Flask to run inside EXE
    env["FLASK_RUN_FROM_EXE"] = "1"

    subprocess.Popen(
        [sys.executable, "app.py"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def run_server():
    t = threading.Thread(target=start_flask)
    t.daemon = True
    t.start()
    time.sleep(2)  # wait for Flask to boot
