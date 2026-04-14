from typing import List
from article import Article
from scrapers.scraper import Scraper
from dataclasses import dataclass
from datetime import datetime
from progress import Progress
from bs4 import BeautifulSoup
import re
import json
import html as HTML


class DataEuropaScraper(Scraper):

    SOURCE: str = "Data.Europa"

    @dataclass
    class Parameters(Scraper.Parameters):
        pass

    def scrape(
        self, parameters: Scraper.Parameters, progress: Progress
    ) -> List[Article]:
        url = self._URL
        html_text = self._get(
            url, progress, f"Fehler beim Scrapen der Quelle: {self.SOURCE}"
        )
        soup = BeautifulSoup(html_text, "html.parser")
        entries = soup.find_all("article")
        articles = []
        for entry in progress.start_iteration(
            entries, total=len(entries), desc="Scraping europa.data articles"
        ):
            date = entry.find("time")
            if date:
                timestamp = datetime.fromisoformat(date.get("datetime"))
                title = entry.find("span").get_text()
                link = f"{self._URL_PREFIX}{entry.find("a").get("href")}"
                content = entry.select_one(".ecl-content-block__description").get_text()

                articles.append(
                    Article(
                        timestamp=timestamp,
                        title=title,
                        medium_organisation=self.SOURCE,
                        content=content,
                        link=link,
                        source=self.SOURCE,
                    )
                )

        return self._filter_dates(articles, parameters)

    _URL_PREFIX: str = "https://data.europa.eu"
    _URL: str = f"{_URL_PREFIX}/en/search"
    _GERMAN_MONTHS: List[str] = [
        "",
        "Januar",
        "Februar",
        "März",
        "April",
        "Mai",
        "Juni",
        "Juli",
        "August",
        "September",
        "Oktober",
        "November",
        "Dezember",
    ]
