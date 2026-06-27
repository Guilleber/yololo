# yololo

A browser-based fact-checking tool. Highlight any text on a webpage, click the **➤** button, and get a short community-note-style verdict (≤ 140 characters) powered by a live web search + LLM.

No Python server required — the extension calls the APIs directly.

---

## How it works

```
Firefox (highlight text)
  → content.js → background.js
  → Tavily API (web search, 5 results)
  → Gemini or OpenAI API (LLM verdict)
  → tooltip with verdict + source links
```

---

## Setup

### 1. Get API keys

| Key | Where to get it | Required |
|-----|----------------|----------|
| **Tavily** | [app.tavily.com](https://app.tavily.com) — free tier: 1 000 searches/month | Always |
| **Gemini** | [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) — free quota | For Gemini model |
| **OpenAI** | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) — pay-as-you-go | For GPT-4o Mini |

### 2. Load the extension in Firefox

1. Go to `about:debugging` → **This Firefox** → **Load Temporary Add-on**
2. Select any file inside the `Firefox_Extension/` folder
3. The yololo icon appears in your toolbar

### 3. Configure

Click the toolbar icon. Paste your API keys and choose a model. Keys are saved locally in `browser.storage.local` — they never leave your browser except in the API calls themselves.

The dot in the top-right turns **green** once the required keys for the selected model are set.

---

## Usage

Select any text on a webpage → click **➤** → verdict appears with source links.

---

## Models

| Key | Provider | Cost |
|-----|----------|------|
| `gemini-2.5-flash` | Google | Free tier available |
| `gpt-4o-mini` | OpenAI | ~$0.15 / 1M tokens |

---

## Project structure

```
Firefox_Extension/
  manifest.json   — permissions, host_permissions for API endpoints
  background.js   — Tavily search + LLM call
  content.js      — injects ➤ button, renders verdict tooltip
  popup.html/js   — settings UI (model + API keys)
```

The `src/` directory and Python files (`server.py`, `server_launcher.py`) are kept for reference but are no longer required to run the extension.
