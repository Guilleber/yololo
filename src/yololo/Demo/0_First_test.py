# First test of simple application to show how the different part connect together

from src.yololo.domain.enums import LLMS_FACTORY

llm=LLMS_FACTORY['QWEN_25_3B']("Qwen/Qwen2.5-3B-Instruct")