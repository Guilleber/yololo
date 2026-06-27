# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Instructions for Claude

- **After any significant change** (new feature, new backend, changed config schema, changed CLI flags, changed setup steps), update `README.md` to reflect it.

## What this project is

Yololo is a fact-checking tool. A Firefox extension lets users highlight text on any webpage; clicking the "➤" button sends the text to a local Python server, which queries a ChromaDB vector database of news articles and passes the most relevant ones to an LLM to generate a short (≤140 character) community-note-style verdict.

## Commands

**Install (editable, from repo root):**
```bash
pip install -e src/
```

**Run the main inference server (port 5000):**
```bash
python server.py --model gpt-4o-mini   # or: qwen-0.6b, qwen-4b
```

**Run the launcher/control server (port 8000) — used by the Firefox extension popup to start/stop server.py:**
```bash
python server_launcher.py
```

**Run the CLI interactive loop (HuggingFace only):**
```bash
python src/yololo/main.py --model Qwen/Qwen3-4B
```

**Load the Firefox extension:**
Go to `about:debugging` → This Firefox → Load Temporary Add-on → pick any file in `Firefox_Extension/`.

**Autostart setup (systemd):**
```bash
bash setup_autostart.sh
```

## Environment variables

Store in `src/.env` (loaded automatically via `python-dotenv`):
- `OPENAI_API_KEY` — required for the `gpt-4o-mini` model
- `GUARDIAN_API_KEY` — required for The Guardian API client

## Architecture

### Request flow
```
Firefox content.js
  → (chrome.runtime.sendMessage) → background.js
  → POST http://localhost:5000
  → server.py (BaseHTTPRequestHandler)
  → ChromaDBStorage.query()  ← top-2 docs by cosine distance across all collections
  → ILargeLanguageModel.call()
  → JSON response back to content.js tooltip
```

The Firefox popup talks to `server_launcher.py` on port 8000 (Flask) to start/stop `server.py` as a subprocess.

### LLM backends (`src/yololo/llm/`)

- `ILargeLanguageModel` — abstract base with a single `call(system_prompt, user_prompt) -> str`
- `HuggingFaceModel` — loads model fresh on each call, clears CUDA cache after; intended for local GPU inference
- `OpenaiApi` — thin wrapper around the OpenAI client; reads `OPENAI_API_KEY` from env

The active model is selected at startup via `--model`, looked up by key in `src/config.yaml` which maps keys to `module_name`, `class_name`, and `args`. To add a new model: add an entry to `config.yaml` and implement `ILargeLanguageModel`.

### Storage (`src/yololo/storage/ChromDB.py`)

`ChromaDBStorage` wraps a ChromaDB `PersistentClient` (stored in `./chroma_db/`). It creates one collection per `Source` enum member on init. Documents are deduplicated by MD5 of `title + source + link`.

`update_database()` spawns one `multiprocessing.Process` per source (using `spawn` start method, required because ChromaDB clients are not fork-safe). Progress is reported via a `Queue`.

`query()` queries every collection, merges results, sorts by distance, and returns the top 2 `Document` objects.

### News sources (`src/yololo/clients/` + `src/yololo/domain/`)

`IClient` defines `stream_newest() -> Iterator[Document]` and `retrieve_rss_flux()`.

`Source` (enum in `domain/source_directory.py`) maps names to client classes. Each enum value's `.value()` is the client constructor — calling `source.value()` instantiates the client. To add a new source: implement `IClient`, add it to the `Source` enum.

Current sources:
- `THE_GUARDIAN` — Guardian Content API (paginated, requires API key)
- `THE_GUARDIAN_RSS` — Guardian international RSS feed (no key needed)

### Firefox extension (`Firefox_Extension/`)

- `content.js` — injects button on text selection; routes LLM requests through `background.js` (avoids CORS)
- `background.js` — receives `sendToLLM` messages, POSTs to `localhost:5000`, returns response
- `popup.js` — calls `localhost:8000/start` and `/stop` to control `server.py`
- Hard-coded host permissions: `http://localhost:5000/`