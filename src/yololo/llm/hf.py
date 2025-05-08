from yololo.llm.llm import ILargeLanguageModel


class HuggingFaceModel(ILargeLanguageModel):
    def __init__(self, model_id: str, **kwargs):
        raise NotImplementedError

    def call(self, system_prompt: str, user_prompt: str) -> str:
        raise NotImplementedError
