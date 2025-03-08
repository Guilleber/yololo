from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from yololo.domain.enums import Language, Source


@dataclass(frozen=True)
class Document:
    link: str
    title: str
    content: str
    pub_date: datetime | None = None
    language: Language | None = None
    source: Source | None = None
