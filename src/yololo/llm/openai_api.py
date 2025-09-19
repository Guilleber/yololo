import os
from typing import Sequence, Tuple, Dict

from openai import OpenAI
from dotenv import load_dotenv

from yololo.llm.llm import ILargeLanguageModel


class OpenaiApi(ILargeLanguageModel):
    def __init__(self,
                 model_id: str) -> None:
        """
        Initializes the openai api class with the due model id and api key
        """
        load_dotenv()
        self.api_key = os.environ["OPENAI_API_KEY"]
        self.model_id = model_id
        self.client = OpenAI(api_key=self.api_key)
        return

    def call(self,
             user_prompt: str,
             system_prompt: str = "You are a helpful assistant.",
             history: Sequence[Tuple[str, str]] | Sequence[Dict[str, str]] | None = None,
             **kwargs,
             ) -> str:
        history = [] if history is None else history
        conversation_history = []
        for turn in history:
            if turn is isinstance(turn, Sequence):
                conversation_history.append({"role": "user", "content": turn[0]})
                conversation_history.append({"role": "assistant", "content": turn[1]})
            elif isinstance(turn, Dict):
                conversation_history.append(turn)
        # prepare the model input
        messages = [
            {"role": "system", "content": system_prompt},
            *conversation_history,
            {"role": "user", "content": user_prompt}
        ]

        completion = self.client.chat.completions.create(
            model=self.model_id,
            messages=messages,
            **kwargs
        )
        content = completion.choices[0].message.content
        return content
