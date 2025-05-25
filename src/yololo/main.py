import argparse

from yololo.llm.hf import HuggingFaceModel
from yololo.storage.ChromDB import ChromaDBStorage
from yololo.domain.document import Document


def main(arguments: argparse.Namespace):
    storage=ChromaDBStorage()

    storage.add_rss('https://www.theguardian.com/international/rss')

    #TODO Save DB
    #TODO mechanic to update DB for a given client

    hf_mod = HuggingFaceModel(model_id=arguments.model)
    while True:
        user_input = input("Enter your prompt: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        system_prompt = ("You are a community note creator, tasked to fact check posts based on provided news from a database. "
                         "Answer only based on provided news articles. If there is no relevant information in the provided articles, say you couldn't find relevant information, don't invent. ")
        database = storage.query(user_input)['documents']

        final_prompt=f"Post : {user_input}. Relevant news articles : {database}"


        response = hf_mod.call(system_prompt, final_prompt)
        print(f"Response: {response}")


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
    args = parser.parse_args()
    main(args)
    
