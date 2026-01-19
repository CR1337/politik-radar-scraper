from typing import List
from article import Article
from scrapers.scraper import Scraper
from dataclasses import dataclass
from datetime import datetime
import requests
from bs4 import BeautifulSoup 
from progress import Progress


class NkrScraper(Scraper):

    SOURCE: str = "Normenkontrollrat"

    @dataclass
    class Parameters(Scraper.Parameters):
        pass

    def scrape(self, parameters: Scraper.Parameters, progress: Progress) -> List[Article]:
        response = requests.get(self._URL)
        response.raise_for_status()
        html = response.text

        soup = BeautifulSoup(html, "html.parser")

        generic_table = soup.find("div", class_="generictable")
        assert generic_table is not None

        entries = generic_table.find_all("div", class_="small-12 large-4 column")
        assert entries

        articles = []
        for entry in progress.start_iteration(entries, total=len(entries), desc="Scraping NKR articles"):
            link_a = entry.find("a", class_="c-teaser__link")
            title_h3 = entry.find("h3", class_="c-teaser__headline")
            content_p = entry.find_next("p", class_=False)
            date_span = entry.find("span", class_="c-teaser__date")

            assert link_a
            assert title_h3
            assert content_p
            assert date_span

            link = f"{self._URL_PREFIX}{str(link_a['href'])}"
            title = title_h3.text
            content = content_p.text
            date_str = date_span.text

            day, month, year = date_str.split(" ")
            day = int(day.strip("."))
            month = self._GERMAN_MONTHS.index(month)
            year = int(year)

            articles.append(Article(
                datetime(year=year, month=month, day=day),
                title=title,
                content=content,
                link=link, 
                source=self.SOURCE
            ))

        return self._filter_dates(articles, parameters)

    _URL_PREFIX: str = "https://www.normenkontrollrat.bund.de/"
    _URL: str = f"{_URL_PREFIX}Webs/NKR/DE/veroeffentlichungen/Presse/pressemitteilungen_node.html"
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
        "Dezember"
    ]
