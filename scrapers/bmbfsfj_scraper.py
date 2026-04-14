from typing import List
from article import Article
from scrapers.scraper import Scraper
from dataclasses import dataclass
from datetime import datetime
from bs4 import BeautifulSoup
from progress import Progress


class BmbfsfjScraper(Scraper):

    SOURCE: str = "BMBFSFJ"

    @dataclass
    class Parameters(Scraper.Parameters):
        pass

    def scrape(
        self, parameters: Scraper.Parameters, progress: Progress
    ) -> List[Article]:
        html_text = self._get(
            self._URL, progress, f"Fehler beim Scrapen der Quelle: {self.SOURCE}"
        )
        if html_text is None:
            return []

        soup = BeautifulSoup(html_text, "html.parser")

        rows = soup.find_all("a", {"class": "text-link"})
        links = []
        for row in rows:
            links.append(f"{self._URL_PREFIX}{row.get('href')}")
        articles = []
        for link in progress.start_iteration(
            links, len(links), "Scraping bmbfsfj articles..."
        ):
            html_article = self._get(
                link, progress, f"Fehler beim Scrapen der Quelle: {self.SOURCE}"
            )
            assert html_article
            soup = BeautifulSoup(html_article, "html.parser")
            title_tag = soup.find("title")
            assert title_tag
            title = title_tag.get_text(strip=True)
            time_tag = soup.find("time")
            assert time_tag
            datetime_string = time_tag.get("datetime")
            assert isinstance(datetime_string, str)
            timestamp = datetime.fromisoformat(datetime_string)
            teaser_p = soup.find("p", class_="article-teaser")
            assert teaser_p
            content = teaser_p.get_text(strip=True)
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

    _URL_PREFIX: str = "https://www.bmbfsfj.bund.de/"
    _URL: str = f"{_URL_PREFIX}bmbfsfj/aktuelles/alle-meldungen"
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
