from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Article:
    timestamp: datetime
    title: str
    content: str
    link: str
    source: str

    