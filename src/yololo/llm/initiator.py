
from yololo.llm.hf import HuggingFaceModel
from yololo.llm.openai_api import OpenaiApi
from yololo.llm.llm import ILargeLanguageModel


def get_llm(model_id: str) -> ILargeLanguageModel:
    if [gn for gn in ["gpt", "o1", "o3", "o4"] if gn in model_id.lower()]:
        llm = OpenaiApi(model_id=model_id)
    else:
        llm = HuggingFaceModel(model_id=model_id)
    return llm
