const dot = document.getElementById("statusDot");
const modelSelect = document.getElementById("modelSelect");
const logDiv = document.getElementById("log");

function setLog(msg, type = "info") {
  logDiv.innerHTML = `<span class="${type === "ok" ? "ok" : type === "err" ? "err" : ""}">${msg}</span>`;
}

function setStatus(running) {
  dot.className = "status-dot " + (running ? "running" : "stopped");
}

// Restore saved model selection
const savedModel = localStorage.getItem("yololo_model");
if (savedModel) modelSelect.value = savedModel;

modelSelect.addEventListener("change", () => {
  localStorage.setItem("yololo_model", modelSelect.value);
});

// Check status on open
fetch("http://127.0.0.1:8200/status")
  .then(r => r.json())
  .then(data => {
    setStatus(data.running);
    if (data.running && data.model) {
      setLog(`Running: ${data.model}`, "ok");
      modelSelect.value = data.model;
    }
  })
  .catch(() => setStatus(false));

document.getElementById("startServer").addEventListener("click", async () => {
  const model = modelSelect.value;
  localStorage.setItem("yololo_model", model);
  setLog("Starting…");
  try {
    const res = await fetch("http://127.0.0.1:8200/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model })
    });
    const data = await res.json();
    if (data.status === "started" || data.status === "already_running") {
      setStatus(true);
      setLog(data.status === "started" ? `Started: ${model}` : `Already running: ${data.model || model}`, "ok");
    } else {
      setLog(data.error || "Failed to start", "err");
    }
  } catch (err) {
    setStatus(false);
    setLog("Cannot reach launcher — is server_launcher.py running?", "err");
  }
});

document.getElementById("stopServer").addEventListener("click", async () => {
  setLog("Stopping…");
  try {
    const res = await fetch("http://127.0.0.1:8200/stop", { method: "POST" });
    const data = await res.json();
    setStatus(false);
    setLog("Stopped", "ok");
  } catch (err) {
    setLog("Cannot reach launcher", "err");
  }
});
