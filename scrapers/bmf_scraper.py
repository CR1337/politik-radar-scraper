from typing import List
from article import Article
from scrapers.scraper import Scraper
from dataclasses import dataclass
from datetime import datetime
from progress import Progress
from bs4 import BeautifulSoup


class BmfScraper(Scraper):

    SOURCE: str = "BMF"

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
        rows = soup.find_all("div", {"class": "bmf-entry"})
        entries = []
        for row in rows:
            if row:
                time_tag = row.find("time")
                a_ref = row.find("a")
                if not time_tag or not a_ref:
                    continue
                datetime_string = time_tag.get("datetime")
                assert isinstance(datetime_string, str)
                timestamp = datetime.fromisoformat(datetime_string)
                link = a_ref.get("href")
                span = a_ref.find("span")
                title = span.get_text(strip=True) if span else "Kein Titel"
                entries.append((timestamp, title, link))
        articles = []
        print(articles)
        for timestamp, title, link in progress.start_iteration(
            entries, total=len(entries), desc="Scraping Bmf articles"
        ):
            url = f"{self._URL_PREFIX}{link}"
            html = self._get(
                url,
                progress,
                f"Fehler beim Scrapen der Quelle: {self.SOURCE} bei Artikel: {title}",
            )
            if html is None:
                continue

            soup = BeautifulSoup(html, "html.parser")

            article_text = soup.find("div", {"class": "article-content-wrapper"})
            if article_text:
                ps = article_text.find_all("p")
                content = "\n\n".join([p.text for p in ps])
                articles.append(
                    Article(
                        timestamp=timestamp,
                        title=title,
                        medium_organisation=self.SOURCE,
                        content=content,
                        link=url,
                        source=self.SOURCE,
                    )
                )

        assert articles

        return self._filter_dates(articles, parameters)

    _URL_PREFIX: str = "https://www.bundesfinanzministerium.de/"
    _URL: str = f"{_URL_PREFIX}Web/DE/Presse/Pressemitteilungen/pressemitteilungen.html"
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
