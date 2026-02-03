from typing import List
from article import Article
from scrapers.scraper import Scraper
from dataclasses import dataclass
from datetime import datetime
from bs4 import BeautifulSoup 
from bs4.element import Tag
from progress import Progress


class DiwScraper(Scraper):

    SOURCE: str = "DIW"

    @dataclass
    class Parameters(Scraper.Parameters):
        pass

    def scrape(self, parameters: Scraper.Parameters, progress: Progress) -> List[Article]:
        html = self._get(self._URL, progress, f"Fehler beim Scrapen der Quelle: {self.SOURCE}")
        if html is None:
            return []

        soup = BeautifulSoup(html, "html.parser")

        ul = soup.find("ul", class_="col-lg-8 col-sm-12")
        assert ul
        lis = ul.find_all("li", class_="teaser_item")

        articles = []
        for li in progress.start_iteration(lis, len(lis), "Scraping DIW articles..."):
            article_type_div = li.find("div", class_="teaser_subline topline")
            assert article_type_div
            article_type = article_type_div.text
            if article_type == "Stellenangebot":
                continue

            h4 = li.find("h4", class_="teaser_header")
            assert h4
            a = h4.find("a")
            assert a

            link = self._URL_PREFIX + a.get("href")
            title = a.text

            content_p = li.find("p", class_="teaser_body")
            assert content_p
            content = content_p.text

            date_span = li.find("span", class_="teaser_date")
            assert date_span
            day, month, year = [int(x) for x in date_span.text.split(".")]
            timestamp = datetime(day=day, month=month, year=year)

            articles.append(Article(
                timestamp=timestamp,
                title=title,
                medium_organisation=self.SOURCE,
                content=content,
                link=link, 
                source=self.SOURCE
            ))

        return self._filter_dates(articles, parameters)


    _URL_PREFIX: str = "https://www.diw.de/"
    _URL: str = f"{_URL_PREFIX}de/diw_01.c.618106.de/nachrichten.html"
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
