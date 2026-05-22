import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

from yololo.llm.llm import ILargeLanguageModel


class GeminiApi(ILargeLanguageModel):
    def __init__(self, model_id: str) -> None:
        load_dotenv()
        self.model_id = model_id
        self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    def call(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt
            )
        )
        return response.text
