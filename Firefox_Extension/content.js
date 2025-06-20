let button = null;
let lastSelectedText = "";

function showTooltip(x, y, text) {
  // Remove any previous tooltip
  const existing = document.querySelector("#my-llm-tooltip");
  if (existing) existing.remove();

  const box = document.createElement("div");
  box.id = "my-llm-tooltip";
  box.textContent = text;

  box.style.position = "absolute";
  box.style.left = `${x}px`;
  box.style.top = `${y}px`;
  box.style.maxWidth = "300px";
  box.style.background = "#fefefe";
  box.style.border = "1px solid #ccc";
  box.style.borderRadius = "8px";
  box.style.boxShadow = "0 4px 12px rgba(0, 0, 0, 0.15)";
  box.style.padding = "12px";
  box.style.fontSize = "14px";
  box.style.lineHeight = "1.5";
  box.style.fontFamily = "Arial, sans-serif";
  box.style.color = "#333";
  box.style.zIndex = "9999";

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

        // Send to local server
        fetch("http://localhost:5000", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ text: lastSelectedText })
        })
        .then(response => response.json())
        .then(data => {
          showTooltip(x, y + 30, data.message);
        })
        .catch(err => {
          console.error("Error talking to local server:", err);
          showTooltip(x, y + 30, "❌ Failed to connect to server");
        });
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
