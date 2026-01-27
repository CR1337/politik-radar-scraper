from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
import requests
from article import Article
from typing import Dict, List
from progress import Progress


class Scraper(ABC):

    SOURCE: str

    @dataclass
    class Parameters(ABC):
        start_date: datetime
        end_date: datetime

    def __init__subclass__(cls, **_) -> None:  # type: ignore
        super().__init_subclass__()
        parameters_class = getattr(cls, "Parameters", None) 
        assert isinstance(parameters_class, type)
        assert issubclass(parameters_class, Scraper.Parameters)

    def _get(self, url: str, progress: Progress, error_message: str, parameters: Dict[str, str] | None = None) -> str | None:
        try:
            response = requests.get(url, params=parameters)
            response.raise_for_status()
            html = response.text
        except Exception:
            progress.add_error_message(error_message)
            return None
        return html

    def _filter_dates(
        self, 
        articles: List[Article], 
        parameters: Scraper.Parameters
    ) -> List[Article]:
        return [
            a for a in articles
            if parameters.start_date <= a.timestamp <= parameters.end_date
        ]


    @abstractmethod
    def scrape(self, parameters: Scraper.Parameters, progress: Progress) -> List[Article]:
        raise NotImplementedError("@abstractmethod")
