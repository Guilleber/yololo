const dot = document.getElementById("statusDot");
const modelSelect = document.getElementById("modelSelect");
const retrievalSelect = document.getElementById("retrievalSelect");
const logDiv = document.getElementById("log");

function setLog(msg, type = "info") {
  logDiv.innerHTML = `<span class="${type === "ok" ? "ok" : type === "err" ? "err" : ""}">${msg}</span>`;
}

function setStatus(state) {
  // state: true (running), false (stopped), "starting"
  if (state === "starting") {
    dot.className = "status-dot starting";
  } else {
    dot.className = "status-dot " + (state ? "running" : "stopped");
  }
}

async function waitUntilReady() {
  for (let i = 0; i < 120; i++) {
    await new Promise(r => setTimeout(r, 1000));
    try {
      const res = await fetch("http://127.0.0.1:8200/ready");
      const data = await res.json();
      if (data.ready) return;
      if (data.reason === "not_started") throw new Error("Server process exited unexpectedly — check my_log_file.log");
    } catch (e) {
      if (e.message.startsWith("Server process")) throw e;
    }
  }
  throw new Error("Server did not become ready after 120 s");
}

async function startServer(model, retrieval) {
  setLog("Starting…");
  setStatus("starting");
  const res = await fetch("http://127.0.0.1:8200/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model, retrieval })
  });
  const data = await res.json();
  if (data.status === "started") {
    setLog("Waiting for server…");
    try {
      await waitUntilReady();
    } catch (e) {
      setStatus(false);
      setLog(e.message, "err");
      return;
    }
    setStatus(true);
    setLog(`Running: ${model} · ${retrieval}`, "ok");
  } else if (data.status === "already_running") {
    setStatus(true);
    setLog(`Already running: ${data.model || model} · ${data.retrieval || retrieval}`, "ok");
  } else {
    setStatus(false);
    setLog(data.error || "Failed to start", "err");
  }
}

// Restore saved selections
const savedModel = localStorage.getItem("yololo_model");
if (savedModel) modelSelect.value = savedModel;
const savedRetrieval = localStorage.getItem("yololo_retrieval");
if (savedRetrieval) retrievalSelect.value = savedRetrieval;

async function restartIfRunning(label) {
  try {
    const statusRes = await fetch("http://127.0.0.1:8200/status");
    const statusData = await statusRes.json();
    if (!statusData.running) return;

    setLog(`Switching ${label}…`);
    setStatus("starting");
    await fetch("http://127.0.0.1:8200/stop", { method: "POST" });
    await startServer(modelSelect.value, retrievalSelect.value);
  } catch (e) {}
}

modelSelect.addEventListener("change", async () => {
  localStorage.setItem("yololo_model", modelSelect.value);
  await restartIfRunning("model");
});

retrievalSelect.addEventListener("change", async () => {
  localStorage.setItem("yololo_retrieval", retrievalSelect.value);
  await restartIfRunning("retrieval");
});

// Check status on open
fetch("http://127.0.0.1:8200/status")
  .then(r => r.json())
  .then(data => {
    setStatus(data.running);
    if (data.running && data.model) {
      modelSelect.value = data.model;
      if (data.retrieval) retrievalSelect.value = data.retrieval;
      setLog(`Running: ${data.model} · ${data.retrieval || "search"}`, "ok");
    }
  })
  .catch(() => setStatus(false));

document.getElementById("startServer").addEventListener("click", async () => {
  const model = modelSelect.value;
  const retrieval = retrievalSelect.value;
  localStorage.setItem("yololo_model", model);
  localStorage.setItem("yololo_retrieval", retrieval);
  try {
    await startServer(model, retrieval);
  } catch (err) {
    setStatus(false);
    setLog("Cannot reach launcher — is server_launcher.py running?", "err");
  }
});

document.getElementById("stopServer").addEventListener("click", async () => {
  setLog("Stopping…");
  try {
    await fetch("http://127.0.0.1:8200/stop", { method: "POST" });
    setStatus(false);
    setLog("Stopped", "ok");
  } catch (err) {
    setLog("Cannot reach launcher", "err");
  }
});
