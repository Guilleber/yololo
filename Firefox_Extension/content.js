let button = null;
let lastSelectedText = "";

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

  button.addEventListener("mousedown", () => {
    if (lastSelectedText.trim() !== "") {
      console.log("Mouseup triggered");
        console.log("Selected:", lastSelectedText);
      alert(`Selected text: "${lastSelectedText}"`);
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
