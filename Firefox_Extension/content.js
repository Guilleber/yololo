let button = null;
let lastSelectedText = "";

function showTooltip(x, y, text) {
  const existing = document.querySelector("#my-llm-tooltip");
  if (existing) existing.remove();

  const box = document.createElement("div");
  box.id = "my-llm-tooltip";

  Object.assign(box.style, {
    position: "absolute", left: `${x}px`, top: `${y}px`,
    maxWidth: "320px", background: "#fefefe", border: "1px solid #ccc",
    borderRadius: "8px", boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
    padding: "12px", fontSize: "14px", lineHeight: "1.5",
    fontFamily: "Arial, sans-serif", color: "#333", zIndex: "9999",
  });

  box.textContent = text;
  document.body.appendChild(box);
}

function showResult(x, y, data) {
  const existing = document.querySelector("#my-llm-tooltip");
  if (existing) existing.remove();

  const box = document.createElement("div");
  box.id = "my-llm-tooltip";

  Object.assign(box.style, {
    position: "absolute", left: `${x}px`, top: `${y}px`,
    maxWidth: "320px", background: "#fefefe", border: "1px solid #ccc",
    borderRadius: "8px", boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
    padding: "12px", fontSize: "14px", lineHeight: "1.5",
    fontFamily: "Arial, sans-serif", color: "#333", zIndex: "9999",
  });

  // Verdict
  const verdict = document.createElement("p");
  verdict.textContent = data.message;
  Object.assign(verdict.style, { margin: "0 0 10px 0" });
  box.appendChild(verdict);

  // Sources
  if (data.source_count > 0) {
    const hr = document.createElement("hr");
    Object.assign(hr.style, { border: "none", borderTop: "1px solid #e0e0e0", margin: "0 0 8px 0" });
    box.appendChild(hr);

    const meta = document.createElement("p");
    meta.textContent = `${data.source_count} source${data.source_count !== 1 ? "s" : ""} consulted`;
    Object.assign(meta.style, { margin: "0 0 6px 0", fontSize: "12px", color: "#888" });
    box.appendChild(meta);

    (data.sources || []).forEach(src => {
      const row = document.createElement("div");
      Object.assign(row.style, { marginBottom: "4px", fontSize: "12px" });

      let domain = src.url;
      try { domain = new URL(src.url).hostname.replace(/^www\./, ""); } catch (_) {}

      const link = document.createElement("a");
      link.href = src.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = src.title ? `${src.title} (${domain})` : domain;
      Object.assign(link.style, { color: "#1a73e8", textDecoration: "none", wordBreak: "break-word" });
      link.addEventListener("mouseover", () => link.style.textDecoration = "underline");
      link.addEventListener("mouseout",  () => link.style.textDecoration = "none");

      row.appendChild(link);
      box.appendChild(row);
    });
  }

  document.body.appendChild(box);
}

function createButton(x, y, lastSelectedText) {
  removeButton();

  button = document.createElement("button");
  button.textContent = "➤";
  button.style.position = "absolute";
  button.style.left = `${x + 5}px`;
  button.style.top = `${y + 5}px`;
  button.style.zIndex = "9999";
  button.style.padding = "4px 6px";
  button.style.fontSize = "14px";
  button.style.cursor = "pointer";
  button.style.background = "#007bff";
  button.style.color = "#fff";
  button.style.border = "none";
  button.style.borderRadius = "4px";
  button.style.boxShadow = "0 2px 6px rgba(0, 0, 0, 0.2)";

//  button.addEventListener("mousedown", () => {
//    if (lastSelectedText.trim() !== "") {
//      showTooltip(x, y + 30, lastSelectedText); // appears just below the button
//    }
//  });

    button.addEventListener("mousedown", () => {
      if (lastSelectedText.trim() !== "") {
        // Show loading tooltip
        showTooltip(x, y + 30, "Loading...");

//        // Send to local server
//        fetch("http://localhost:5000", {
//          method: "POST",
//          headers: {
//            "Content-Type": "application/json"
//          },
//          body: JSON.stringify({ text: lastSelectedText })
//        })
//        .then(response => response.json())
//        .then(data => {
//          showTooltip(x, y + 30, data.message);
//        })
//        .catch(err => {
//          console.error("Error talking to local server:", err);
//          showTooltip(x, y + 30, "❌ Failed to connect to server");
//        });
        chrome.runtime.sendMessage(
          { type: "sendToLLM", text: lastSelectedText },
          (response) => {
            if (response && response.success) {
              showResult(x, y + 30, response.data);
            } else {
              const msg = response?.error || "Unknown error";
              console.error("LLM error:", msg);
              showTooltip(x, y + 30, "❌ " + msg);
            }
          }
        );
      }
    });


  document.body.appendChild(button);
}

function removeButton() {
  if (button) {
    button.remove();
    button = null;
  }
  lastSelectedText = "";
}

document.addEventListener("mouseup", (event) => {
  const selection = window.getSelection();
  const text = selection.toString().trim();



  if (text.length > 0) {
    lastSelectedText = text;
    const rect = selection.getRangeAt(0).getBoundingClientRect();
    createButton(rect.right + window.scrollX, rect.top + window.scrollY, lastSelectedText);
  } else {
    removeButton();
  }
});

document.addEventListener("scroll", removeButton);
document.addEventListener("mousedown", (e) => {
  if (button && !button.contains(e.target)) {
    removeButton();
  }
});

document.addEventListener("click", (e) => {
  const tooltip = document.querySelector("#my-llm-tooltip");
  if (tooltip && !tooltip.contains(e.target) && e.target !== button) {
    tooltip.remove();
  }
});
