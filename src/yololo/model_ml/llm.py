from yololo.domain.models import LLM


class LargeLanguageModel:
    def __init__(self):
        raise NotImplementedError

    def query_llm(self, llm: LLM):
        raise NotImplementedError
