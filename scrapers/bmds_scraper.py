from typing import List
from article import Article
from scrapers.scraper import Scraper
from dataclasses import dataclass
from datetime import datetime
from bs4 import BeautifulSoup 
from bs4.element import Tag
from progress import Progress


class BmdsScraper(Scraper):

    SOURCE: str = "BMDS"

    @dataclass
    class Parameters(Scraper.Parameters):
        pass

    def scrape(self, parameters: Scraper.Parameters, progress: Progress) -> List[Article]:
        html = self._get(self._URL, progress, f"Fehler beim Scrapen der Quelle: {self.SOURCE}")
        if html is None:
            return []

        soup = BeautifulSoup(html, "html.parser")

        ol = soup.find("ol", class_="results-list list-unstyled")
        assert ol
        lis = ol.find_all("li")

        articles = []
        for li in progress.start_iteration(lis, len(lis), "Scraping BMDS articles..."):
            date_span = li.find("span", class_="date-text")
            assert date_span
            date_string = "".join(c for c in date_span.text if c in "0123456789.")
            day, month, year = [int(x) for x in date_string.split(".")]
            timestamp = datetime(day=day, month=month, year=year)

            a = li.find("a", class_="stretched-link teaser-link")
            assert a
            link = self._URL_PREFIX + a.get("href")
            
            title_span = a.find("span")
            assert title_span
            title = title_span.text

            sub_html = self._get(link, progress, f"Fehler beim Scrapen der Quelle: {self.SOURCE} bei Artikel: {title}")
            if sub_html is None:
                return []

            sub_soup = BeautifulSoup(sub_html, "html.parser")

            content_div = sub_soup.find("div", class_="ce-bodytext")
            assert content_div
            ps = content_div.find_all("p")
            assert len(ps) > 1
            content = ps[1].text

            articles.append(Article(
                timestamp=timestamp,
                title=title,
                medium_organisation=self.SOURCE,
                content=content,
                link=link, 
                source=self.SOURCE
            ))

        return self._filter_dates(articles, parameters)


    _URL_PREFIX: str = "https://bmds.bund.de/"
    _URL: str = f"{_URL_PREFIX}aktuelles/pressemitteilungen"
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
