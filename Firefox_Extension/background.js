browser.runtime.onMessage.addListener((request, sender) => {
  if (request.type === "sendToLLM") {
    return fetch("http://localhost:5000", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: request.text })
    })
    .then(res => res.json().then(data => ({ ok: res.ok, data })))
    .then(({ ok, data }) => {
      if (ok) {
        return { success: true, data };
      } else {
        return { success: false, error: data.error || "Server error" };
      }
    })
    .catch(err => {
      const msg = err instanceof TypeError
        ? "Cannot connect to inference server — is it running?"
        : `Network error: ${err.message}`;
      return { success: false, error: msg };
    });
  }
});
