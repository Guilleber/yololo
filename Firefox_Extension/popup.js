const modelSelect  = document.getElementById("modelSelect");
const tavilyInput  = document.getElementById("tavilyKey");
const geminiInput  = document.getElementById("geminiKey");
const openaiInput  = document.getElementById("openaiKey");
const statusDiv    = document.getElementById("status");
const dot          = document.getElementById("statusDot");

// Load saved values
browser.storage.local.get(["llm_model", "tavily_key", "gemini_key", "openai_key"]).then(s => {
  if (s.llm_model)   modelSelect.value = s.llm_model;
  if (s.tavily_key)  tavilyInput.value  = s.tavily_key;
  if (s.gemini_key)  geminiInput.value  = s.gemini_key;
  if (s.openai_key)  openaiInput.value  = s.openai_key;
  updateStatus();
});

// Auto-save on change
modelSelect.addEventListener("change", save);
tavilyInput.addEventListener("input",  save);
geminiInput.addEventListener("input",  save);
openaiInput.addEventListener("input",  save);

function save() {
  browser.storage.local.set({
    llm_model:  modelSelect.value,
    tavily_key: tavilyInput.value.trim(),
    gemini_key: geminiInput.value.trim(),
    openai_key: openaiInput.value.trim(),
  });
  updateStatus();
}

function updateStatus() {
  const model     = modelSelect.value;
  const hasTavily = tavilyInput.value.trim().length > 0;
  const hasLlm    = model.startsWith("gemini")
    ? geminiInput.value.trim().length > 0
    : openaiInput.value.trim().length > 0;

  if (hasTavily && hasLlm) {
    dot.className = "status-dot ready";
    statusDiv.innerHTML = `<span class="ok">Ready — ${model}</span>`;
  } else {
    dot.className = "status-dot missing";
    const missing = [!hasTavily && "Tavily key", !hasLlm && `${model} key`].filter(Boolean).join(", ");
    statusDiv.innerHTML = `<span class="warn">Missing: ${missing}</span>`;
  }
}

// Toggle password visibility
document.querySelectorAll(".key-wrap button").forEach(btn => {
  btn.addEventListener("click", () => {
    const input = document.getElementById(btn.dataset.target);
    input.type = input.type === "password" ? "text" : "password";
  });
});
