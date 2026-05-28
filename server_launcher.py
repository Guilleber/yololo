# server_launcher.py
import subprocess
import os
import sys
from flask import Flask, jsonify, request
import psutil

app = Flask(__name__)

@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

SERVER_PATH = os.path.join(os.path.dirname(__file__), "server.py")
_venv_python = os.path.join(os.path.dirname(__file__), "venv", "bin", "python3")
SERVER_PYTHON = _venv_python if os.path.exists(_venv_python) else sys.executable
process = None
current_model = None

@app.route("/start", methods=["POST"])
def start_server():
    global process, current_model
    body = request.get_json(silent=True) or {}
    model = body.get("model", "gemini-2.5-flash")

    if process is None or process.poll() is not None:
        process = subprocess.Popen([SERVER_PYTHON, SERVER_PATH, "--model", model])
        current_model = model
        return jsonify({"status": "started", "model": model})
    else:
        return jsonify({"status": "already_running", "model": current_model})

@app.route("/status", methods=["GET"])
def status():
    running = process is not None and process.poll() is None
    return jsonify({"running": running, "model": current_model if running else None})

@app.route("/stop", methods=["POST"])
def stop_server():
    global process, current_model
    running, proc = _find_server_proc()
    if running:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except psutil.TimeoutExpired:
            proc.kill()
        process = None
        current_model = None
        return jsonify({"status": "stopped"})
    else:
        return jsonify({"status": "not_running"})

def _find_server_proc():
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and any("server.py" in part for part in cmdline):
                return True, proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False, None

if __name__ == "__main__":
    app.run(port=8200)
