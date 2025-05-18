from enum import Enum
from src.yololo.llms.Qwen25 import Qwen25

class Language(Enum):
    ENGLISH = 'en'
    FRENCH = 'fr'


class Source(Enum):
    THE_GUARDIAN = 'the_guardian'


LLMS_FACTORY={
    "QWEN_25_3B": Qwen25
}