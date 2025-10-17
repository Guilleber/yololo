import json
import argparse
import importlib
from http.server import BaseHTTPRequestHandler, HTTPServer

import yaml

from yololo.llm.llm import ILargeLanguageModel
from yololo.storage.ChromDB import ChromaDBStorage
import threading
import multiprocessing

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

        def do_POST(self):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            data = json.loads(body)

            print("Received:", data)

            # Call the LLM
            user_input = data.get("text", "")
            #TODO : If this gets more complex, we should move this to a RAG class
            system_prompt = (
                "You are a community note creator, tasked to fact check posts based on provided news from a database. "
                "Answer only based on provided news articles. "
                "If there is no relevant information in the provided articles, say you couldn't find relevant information, don't invent. "
                "As a community note creator, your answer should be really short (max 140 characters).")
            database = storage.query(user_input)  # ['documents']

            final_prompt = f"Post : {user_input}. Relevant news articles : {database}"

            response = llm_instance.call(system_prompt, final_prompt)



            print(response)

            response = {"message": response}

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode("utf-8"))

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
