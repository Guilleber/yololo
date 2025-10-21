function logMessage(msg, type = "info") {
  const logDiv = document.getElementById("log");
  const color = type === "error" ? "red" : "green";
  const line = document.createElement("div");
  line.style.color = color;
  line.textContent = msg;
  logDiv.appendChild(line);
  logDiv.scrollTop = logDiv.scrollHeight; // auto-scroll
}

document.getElementById("startServer").addEventListener("click", async () => {
  try {
    const res = await fetch("http://127.0.0.1:8000/start", { method: "POST" });
    const data = await res.json();
    logMessage("✅ Server " + data.status);
  } catch (err) {
    logMessage("❌ Failed to start server: " + err.message, "error");
  }
});

document.getElementById("stopServer").addEventListener("click", async () => {
  try {
    const res = await fetch("http://127.0.0.1:8000/stop", { method: "POST" });
    const data = await res.json();
    logMessage("🛑 Server " + data.status);
  } catch (err) {
    logMessage("❌ Failed to stop server: " + err.message, "error");
  }
});
