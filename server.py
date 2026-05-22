import json
import argparse
import importlib
from http.server import BaseHTTPRequestHandler, HTTPServer

import yaml

from yololo.llm.llm import ILargeLanguageModel
from yololo.storage.ChromDB import ChromaDBStorage
import threading
import multiprocessing
import signal
import sys

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

# Factory to inject LLM into handler
def make_handler_with_llm_and_db(llm_instance: ILargeLanguageModel, storage: ChromaDBStorage) -> None:
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
                print(f"ChromaDB error: {e}")
                self._send_json(503, {"error": f"Database error ({type(e).__name__}): {e}"})
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

            print(response)
            self._send_json(200, {"message": response})

    return SimpleHandler


def main(argdict: argparse.Namespace) -> None:
    storage = ChromaDBStorage()

    # storage.add_rss('https://www.theguardian.com/international/rss')
    def background_update():
        storage.update_database()

    thread = threading.Thread(target=background_update, daemon=True)
    thread.start()

    print("Continuing main program while database updates in background...")

    config_dict = yaml.safe_load(open("src/config.yaml", "r"))
    print(config_dict)
    print(argdict.model)
    llm_mod = importlib.import_module(config_dict["models"][argdict.model]["module_name"])
    llm_class = getattr(llm_mod, config_dict["models"][argdict.model]["class_name"])
    llm = llm_class(**config_dict["models"][argdict.model]["args"])
    # Create the handler class with the LLM preloaded
    HandlerClass = make_handler_with_llm_and_db(llm, storage)

    # Start the server
    httpd = HTTPServer(("localhost", 5000), HandlerClass)
    print("Server running at http://localhost:5000")
    httpd.serve_forever()


if __name__ == "__main__":
    # TODO: CHANGE INTO A PRODUCT FINAL VERSION
    parser = argparse.ArgumentParser(description="YOLOLO: You Only Live Once Like Oesterreicht")
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="Path to the YOLOv8 model file.",
    )
    argdict = parser.parse_args()
    main(argdict)
