from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import json
import argparse

import gc
import torch
from dotenv import load_dotenv

from yololo.llm.openai_api import OpenaiApi
from yololo.llm.hf import HuggingFaceModel
from yololo.llm.llm import ILargeLanguageModel
from yololo.storage.ChromDB import ChromaDBStorage
from yololo.domain.document import Document


class SimpleHandler(BaseHTTPRequestHandler):
    # TODO: This is a very simple handler, not production ready
    def __init__(self, llm_instance: ILargeLanguageModel, storage: ChromaDBStorage):
        self.llm_instance = llm_instance
        self.storage = storage

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
        # TODO : If this gets more complex, we should move this to a RAG class
        # TODO: consider moving all pre-set prompts to it's own file (each) in a ./llm/prompts directory, either json, config, txt or py format
        system_prompt = (
            "You are a community note creator, tasked to fact check posts based on provided news from a database. "
            "Answer only based on provided news articles. "
            "If there is no relevant information in the provided articles, say you couldn't find relevant information, don't invent. "
            "As a community note creator, your answer should be really short (max 140 characters).")
        database = self.storage.query(user_input)  # ['documents']

        final_prompt = f"Post : {user_input}. Relevant news articles : {database}"

        print(33333333333333333333333333333333333333333)
        response = self.llm_instance.call(system_prompt, final_prompt)
        print(444444444444444444444444444444444, response)

        response = {"message": response}

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode("utf-8"))


# Factory to inject LLM into handler
def make_handler_with_llm_and_db(llm_instance: ILargeLanguageModel, storage: ChromaDBStorage) -> SimpleHandler:
    simple_handler = SimpleHandler(llm_instance, storage)
    return simple_handler


def main(argdict: argparse.Namespace) -> None:
    load_dotenv()  # Load environment variables from .env file
    storage = ChromaDBStorage()

    # storage.add_rss('https://www.theguardian.com/international/rss')
    storage.update_database()

    if [gn for gn in ["gpt", "o1", "o3", "o4"] if gn in argdict.model.lower()]:
        llm = OpenaiApi(model_id=argdict.model)
        print(1000000000000000000000000)
    else:
        llm = HuggingFaceModel(model_id=argdict.model)
        print(9999999999999999999999999999999)
    print(111111111111111111111111111111, llm is not None)
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
        default="Qwen/Qwen3-4B",
        help="Path to the YOLOv8 model file.",
    )
    argdict = parser.parse_args()
    main(argdict)
