from __future__ import annotations
from typing import Tuple, List, Dict, Union

from transformers import PreTrainedTokenizer, PreTrainedModel

from yololo.domain.enums import LangModel


class LLM:
    user_prompt: str
    system_prompt: str
    history: Union[List[Tuple[str, str]], None] = None
    auth_tok: str
    local_tokenizer: LangModel | PreTrainedTokenizer | None = None
    local_model: LangModel | PreTrainedModel | None = None
    local_model_device_map: str
    local_model_torch_dtype: str
    local_max_new_tokens: int
    local_quant_config: Dict
