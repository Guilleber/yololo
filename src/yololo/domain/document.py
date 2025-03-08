from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class Language(StrEnum):
    ENGLISH = 'fr'
    FRENCH = 'fr'


@dataclass(frozen=True)
class Document:
    link: str
    title: str
    content: str
    pub_date: datetime | None = None
    language: Language | None = None
