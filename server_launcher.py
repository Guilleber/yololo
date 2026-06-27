# server_launcher.py
import subprocess
import os
import sys
import socket
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

current_retrieval = None

@app.route("/start", methods=["POST"])
def start_server():
    global process, current_model, current_retrieval
    body = request.get_json(silent=True) or {}
    model = body.get("model", "gemini-2.5-flash")
    retrieval = body.get("retrieval", "search")

    if process is None or process.poll() is not None:
        process = subprocess.Popen(
            [SERVER_PYTHON, SERVER_PATH, "--model", model, "--retrieval", retrieval]
        )
        current_model = model
        current_retrieval = retrieval
        return jsonify({"status": "started", "model": model, "retrieval": retrieval})
    else:
        return jsonify({"status": "already_running", "model": current_model, "retrieval": current_retrieval})

@app.route("/status", methods=["GET"])
def status():
    running = process is not None and process.poll() is None
    return jsonify({
        "running": running,
        "model": current_model if running else None,
        "retrieval": current_retrieval if running else None,
    })

@app.route("/ready", methods=["GET"])
def ready():
    if process is None or process.poll() is not None:
        return jsonify({"ready": False, "reason": "not_started"})
    try:
        with socket.create_connection(("127.0.0.1", 5000), timeout=0.5):
            return jsonify({"ready": True})
    except OSError:
        return jsonify({"ready": False, "reason": "not_ready"})

@app.route("/stop", methods=["POST"])
def stop_server():
    global process, current_model, current_retrieval
    stopped = False

    if process is not None and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
        stopped = True
    else:
        # Fallback: find a server.py that was started outside the launcher
        psutil_proc = _find_server_proc()
        if psutil_proc is not None:
            psutil_proc.terminate()
            try:
                psutil_proc.wait(timeout=3)
            except psutil.TimeoutExpired:
                psutil_proc.kill()
            stopped = True

    process = None
    current_model = None
    current_retrieval = None
    return jsonify({"status": "stopped" if stopped else "not_running"})

def _find_server_proc():
    """Return a psutil.Process for server.py if one is running, else None."""
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and any(os.path.basename(part) == "server.py" for part in cmdline):
                return proc
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

if __name__ == "__main__":
    app.run(port=8200)
