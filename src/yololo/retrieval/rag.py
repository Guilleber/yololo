from yololo.llm.llm import LargeLanguageModel
from yololo.storage.storage import DocumentStorage


class RetrievalAugmentedModel:
    def __init__(self):
        raise NotImplementedError

    def rag(self):
        raise NotImplementedError