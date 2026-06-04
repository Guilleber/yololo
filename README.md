# yololo

A browser-based fact-checking tool. Highlight any text on a webpage, click the **➤** button that appears, and get a short community-note-style verdict (≤ 140 characters) powered by an LLM + your choice of retrieval backend.

---

## How it works

```
Firefox (highlight text)
  → content.js → background.js
  → POST localhost:5000
  → server.py
  → IRetrieval.query()        ← web search (Tavily) or local vector DB (ChromaDB)
  → ILargeLanguageModel.call()
  → verdict displayed as tooltip
```

The Firefox extension popup talks to `server_launcher.py` (port 8200) to start/stop `server.py` as a subprocess, so you never need to touch a terminal after initial setup.

---

## Prerequisites

- Python 3.10+
- Firefox
- A virtual environment (recommended)

---

## Installation

```bash
# From the repo root
python -m venv venv
source venv/bin/activate
pip install -e src/
```

---

## API keys

Store all keys in `src/.env` (created manually, never committed). The file is loaded automatically at server startup.

```
# src/.env

TAVILY_API_KEY=        # required for web-search retrieval (default mode)
OPENAI_API_KEY=        # required for the gpt-4o-mini model
GEMINI_API_KEY=        # required for the gemini-2.5-flash model
GUARDIAN_API_KEY=      # required only for the ChromaDB/local-DB retrieval mode
```

### Getting each key

**Tavily** (web search retrieval — recommended)
1. Go to [app.tavily.com](https://app.tavily.com) and create a free account.
2. Your API key is shown on the dashboard. Free tier: 1 000 searches/month.

**OpenAI** (for `gpt-4o-mini`)
1. Go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys).
2. Click **Create new secret key**. Copy it immediately — it won't be shown again.
3. Make sure your account has a positive credit balance (Settings → Billing).

**Gemini** (for `gemini-2.5-flash` — free tier available)
1. Go to [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey).
2. Click **Create API key**. No billing required for the free quota.

**Guardian** (only needed for ChromaDB/local-DB mode)
1. Go to [open-platform.theguardian.com/access](https://open-platform.theguardian.com/access).
2. Register for a developer key. Free, approved within minutes.

---

## Running

### Option A — Extension-controlled (recommended)

1. Start the launcher (only needs to run once; survives server restarts):
   ```bash
   uv run server_launcher.py
   ```
2. Load the extension in Firefox (see below).
3. Use the popup to pick a **model** and **retrieval** mode, then click **▶ Start**. The dot turns amber while loading, then green when ready.

### Option B — Manual

```bash
# Web search retrieval + Gemini (default flags)
python server.py --model gemini-2.5-flash --retrieval search

# Local DB retrieval + GPT-4o Mini
python server.py --model gpt-4o-mini --retrieval db

# Local Qwen model (GPU recommended)
python server.py --model qwen-4b --retrieval search
```

Available `--model` values: `gemini-2.5-flash`, `gpt-4o-mini`, `qwen-0.6b`, `qwen-4b`  
Available `--retrieval` values: `search` (Tavily), `db` (ChromaDB)

### Option C — Autostart via systemd

```bash
bash setup_autostart.sh
```

This installs a systemd service that starts `server_launcher.py` at login so the extension popup always has something to talk to.

---

## Loading the Firefox extension

1. Open Firefox and navigate to `about:debugging`.
2. Click **This Firefox** → **Load Temporary Add-on**.
3. Select any file inside the `Firefox_Extension/` folder.
4. The yololo icon appears in your toolbar.

> The extension is temporary — it must be reloaded after each Firefox restart. For a permanent install, the extension would need to be signed by Mozilla.

---

## Using the extension

1. On any webpage, select some text.
2. A small **➤** button appears near your selection. Click it.
3. A tooltip shows the verdict within a few seconds.

The popup (toolbar icon) lets you:
- Switch LLM model on the fly (auto-restarts the server)
- Switch retrieval backend on the fly (auto-restarts the server)
- Stop the server

---

## Retrieval backends

| Mode | Key | What it does |
|------|-----|--------------|
| `search` | `TAVILY_API_KEY` | Live Tavily web search — always up to date, no local storage needed |
| `db` | `GUARDIAN_API_KEY` | ChromaDB vector store populated from The Guardian API & RSS; runs entirely offline after initial sync |

---

## Adding a new LLM

1. Create `src/yololo/llm/my_model.py` implementing `ILargeLanguageModel.call(system_prompt, user_prompt) -> str`.
2. Add an entry to `src/config.yaml` under `models:`:
   ```yaml
   my-model:
     class_name: MyModel
     module_name: yololo.llm.my_model
     args:
       model_id: some/model-id
   ```
3. Use it: `python server.py --model my-model`

## Adding a new retrieval backend

1. Create `src/yololo/retrieval/my_retrieval.py` implementing `IRetrieval.query(text) -> list[Document]`.
2. Add an entry to `src/config.yaml` under `retrieval:`:
   ```yaml
   my-backend:
     class_name: MyRetrieval
     module_name: yololo.retrieval.my_retrieval
     args:
       api_key: ${MY_API_KEY}
   ```
3. Use it: `python server.py --retrieval my-backend`

---

## Project structure

```
server.py               — main inference server (port 5000)
server_launcher.py      — control server (port 8200); starts/stops server.py
src/
  config.yaml           — model and retrieval backend registry
  .env                  — API keys (not committed)
  yololo/
    llm/                — LLM backends (OpenAI, Gemini, HuggingFace)
    retrieval/          — retrieval backends (Tavily search, ChromaDB)
    storage/            — ChromaDB persistence layer
    clients/            — news source clients (Guardian API, RSS)
    domain/             — Document dataclass, enums
Firefox_Extension/
  content.js            — injects the ➤ button on text selection
  background.js         — proxies requests to localhost:5000 (avoids CORS)
  popup.js / popup.html — server control UI
```
