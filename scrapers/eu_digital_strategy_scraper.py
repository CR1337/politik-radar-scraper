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


class EuDigitalStrategy(Scraper):

    SOURCE: str = "EU Digital Strategy"

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
        entries = soup.find_all("article",{"class":"ecl-content-item ecl-content-item--divider ecl-u-mb-xl"})
        articles = []
        for entry in progress.start_iteration(
            entries, total=len(entries), desc="Scraping EU digital strategy articles"
        ):
            title = entry.find("span").get_text()
            content = entry.find("div",{"class":"cnt-teaser no-media ecl-u-type-m"}).get_text()
            link = f"{self._URL_PREFIX}{entry.find("a").get("href")}"
            items = entry.find_all("li", class_="ecl-content-block__primary-meta-item")
            date_text = items[1].get_text(strip=True)
            day, month_str, year = date_text.split()
            month = self._GERMAN_MONTHS.index(month_str)
            timestamp = datetime(int(year), month, int(day))
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

    _URL_PREFIX: str = "https://digital-strategy.ec.europa.eu"
    _URL: str = f"{_URL_PREFIX}/de/news?type=5%7C13"
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
