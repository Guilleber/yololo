import json
import argparse
import importlib
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

import yaml
from dotenv import load_dotenv

from yololo.llm.llm import ILargeLanguageModel
from yololo.retrieval.base import IRetrieval
import multiprocessing
import signal
import sys
import logging

logging.basicConfig(filename='my_log_file.log', level=logging.INFO)

class LoggerWriter:
    def __init__(self, level):
        self.level = level
    def write(self, message):
        if message.strip():  # ignore empty messages
            self.level(message)
    def flush(self):
        pass  # needed for Python 3 compatibility

# Redirect stdout and stderr
sys.stdout = LoggerWriter(logging.info)
sys.stderr = LoggerWriter(logging.error)

#Make it capture SIGTERM
def handle_sigterm(signum, frame):
    print("SIGTERM received, shutting down...")
    sys.exit(0)

signal.signal(signal.SIGTERM, handle_sigterm)


# always set before threads start
multiprocessing.set_start_method("spawn", force=True)

# Factory to inject LLM and retrieval backend into handler
def make_handler_with_llm_and_db(llm_instance: ILargeLanguageModel, storage: IRetrieval) -> None:
    class SimpleHandler(BaseHTTPRequestHandler):
        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        def _send_json(self, code, payload):
            body = json.dumps(payload).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body)

            print("Received:", data)

            user_input = data.get("text", "")
            system_prompt = (
                "You are a community note creator, tasked to fact check posts based on provided news from a database. "
                "Answer only based on provided news articles. "
                "If there is no relevant information in the provided articles, say you couldn't find relevant information, don't invent. "
                "As a community note creator, your answer should be really short (max 140 characters).")

            try:
                database = storage.query(user_input)
            except Exception as e:
                print(f"Retrieval error: {e}")
                self._send_json(503, {"error": f"Retrieval error ({type(e).__name__}): {e}"})
                return

            final_prompt = f"Post : {user_input}. Relevant news articles : {database}"

            try:
                response = llm_instance.call(system_prompt, final_prompt)
            except Exception as e:
                err_module = type(e).__module__ or ""
                if "openai" in err_module.lower():
                    msg = f"OpenAI API error ({type(e).__name__}): {e}"
                else:
                    msg = f"LLM error ({type(e).__name__}): {e}"
                print(msg)
                self._send_json(502, {"error": msg})
                return

            sources = [
                {"title": doc.title, "url": doc.link}
                for doc in database
                if doc.link
            ]
            print(response)
            self._send_json(200, {
                "message": response,
                "source_count": len(database),
                "sources": sources[:3],
            })

    return SimpleHandler


def _resolve_args(args: dict) -> dict:
    """Expand ${ENV_VAR} placeholders in config args."""
    resolved = {}
    for k, v in args.items():
        if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
            env_var = v[2:-1]
            resolved[k] = os.environ[env_var]
        else:
            resolved[k] = v
    return resolved


def main(argdict: argparse.Namespace) -> None:
    load_dotenv("src/.env")

    config_dict = yaml.safe_load(open("src/config.yaml", "r"))

    # Instantiate retrieval backend
    retrieval_cfg = config_dict["retrieval"][argdict.retrieval]
    retrieval_mod = importlib.import_module(retrieval_cfg["module_name"])
    retrieval_class = getattr(retrieval_mod, retrieval_cfg["class_name"])
    retrieval = retrieval_class(**_resolve_args(retrieval_cfg["args"]))

    # Instantiate LLM
    llm_cfg = config_dict["models"][argdict.model]
    llm_mod = importlib.import_module(llm_cfg["module_name"])
    llm_class = getattr(llm_mod, llm_cfg["class_name"])
    llm = llm_class(**llm_cfg["args"])

    HandlerClass = make_handler_with_llm_and_db(llm, retrieval)

    httpd = HTTPServer(("localhost", 5000), HandlerClass)
    print(f"Server running at http://localhost:5000 (model={argdict.model}, retrieval={argdict.retrieval})")
    httpd.serve_forever()


if __name__ == "__main__":
    # TODO: CHANGE INTO A PRODUCT FINAL VERSION
    parser = argparse.ArgumentParser(description="YOLOLO: You Only Live Once Like Oesterreicht")
    parser.add_argument(
        "-m", "--model",
        type=str,
        default="gpt-4o-mini",
        help="LLM backend key (defined in config.yaml).",
    )
    parser.add_argument(
        "-r", "--retrieval",
        type=str,
        default="search",
        choices=["db", "search"],
        help="Retrieval backend: 'db' (ChromaDB) or 'search' (Tavily).",
    )
    argdict = parser.parse_args()
    main(argdict)
