import argparse

from yololo.llm.hf import HuggingFaceModel
# from yololo.retrieval



def main(arguments: argparse.Namespace):
    hf_mod = HuggingFaceModel(model_id=arguments.model)
    while True:
        user_input = input("Enter your prompt: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        system_prompt = "You are a helpful assistant."
        response = hf_mod.call(system_prompt, user_input)
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
    
