from yololo.llm.llm import ILargeLanguageModel

import torch
# from transformers import pipeline
from transformers import AutoModelForCausalLM, AutoTokenizer

class HuggingFaceModel(ILargeLanguageModel):
    def __init__(self, model_id: str, **kwargs):
        """
        Initializes the HuggingFaceModel with the specified model ID and additional parameters.

        :param model_id: The ID of the Hugging Face model to use.
        :param kwargs: Additional parameters for the model.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype="auto",
            device_map="auto"
        )

    def call(self, system_prompt: str, user_prompt: str) -> str:
        # prepare the model input
        messages = [
            {"role": "user", "content": user_prompt}
        ]
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=True  # Switches between thinking and non-thinking modes. Default is True.
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        # conduct text completion
        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=32768
        )
        output_ids = generated_ids[0][len(model_inputs.input_ids[0]):].tolist()

        # parsing thinking content
        try:
            # rindex finding 151668 (</think>)
            index = len(output_ids) - output_ids[::-1].index(151668)
        except ValueError:
            index = 0

        # thinking_content = tokenizer.decode(output_ids[:index], skip_special_tokens=True).strip("\n")
        content = self.tokenizer.decode(output_ids[index:], skip_special_tokens=True).strip("\n")
        return content
