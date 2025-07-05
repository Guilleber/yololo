chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "sendToLLM") {
    fetch("http://localhost:5000", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: request.text })
    })
    .then(res => res.json())
    .then(data => sendResponse({ success: true, data }))
    .catch(err => sendResponse({ success: false, error: String(err) }));

    return true; // Required to keep sendResponse alive
  }
});