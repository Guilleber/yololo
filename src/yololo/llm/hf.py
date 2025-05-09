from yololo.llm.llm import ILargeLanguageModel

import torch
from transformers import pipeline


class HuggingFaceModel(ILargeLanguageModel):
    def __init__(self, model_id: str, **kwargs):
        """
        Initializes the HuggingFaceModel with the specified model ID and additional parameters.

        :param model_id: The ID of the Hugging Face model to use.
        :param kwargs: Additional parameters for the model.
        """
        self.pipeline = pipeline(
            "text-generation",
            model=model_id,
            tokenizer=model_id,
            device=0 if torch.cuda.is_available() else -1,
            **kwargs
        )

    def call(self, system_prompt: str, user_prompt: str) -> str:
        result = self.pipeline(
            f"{system_prompt} {user_prompt}",
            max_length=512,
            do_sample=True,
            truncation=True,
            top_k=50,
            top_p=0.95,
            num_return_sequences=1,
        )
        return result[0]['generated_text']
    
