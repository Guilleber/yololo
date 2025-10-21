# server_launcher.py
import subprocess
import os
import sys
from flask import Flask, jsonify
import psutil

app = Flask(__name__)

SERVER_PATH = os.path.join(os.path.dirname(__file__), "server.py")
process = None

@app.route("/start", methods=["POST"])
def start_server():
    global process
    if process is None or process.poll() is not None:
        process = subprocess.Popen([sys.executable, SERVER_PATH])
        return jsonify({"status": "started"})
    else:
        return jsonify({"status": "already_running"})

def server_running():
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and any("server.py" in part for part in cmdline):
                return True, proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False, None


@app.route("/stop", methods=["POST"])
def stop_server():
    running, proc = server_running()
    if running:
        proc.terminate()  # graceful
        try:
            proc.wait(timeout=3)
        except psutil.TimeoutExpired:
            proc.kill()  # force kill
        return jsonify({"status": "stopped"})
    else:
        return jsonify({"status": "not_running"})

if __name__ == "__main__":
    app.run(port=8000)
