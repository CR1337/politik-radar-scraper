from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Article:
    timestamp: datetime
    title: str
    medium_organisation: str
    content: str
    link: str
    source: str

    def __eq__(self, other) -> bool:
        return self.title == other.title
    
    def __hash__(self) -> int:
        return hash(self.title)
    