from typing import List
from article import Article
from scrapers.scraper import Scraper
from dataclasses import dataclass
from datetime import datetime
import requests
from bs4 import BeautifulSoup 
from bs4.element import Tag
from progress import Progress


class DscScraper(Scraper):

    SOURCE: str = "Digital Services Coordinator"

    @dataclass
    class Parameters(Scraper.Parameters):
        pass

    def scrape(self, parameters: Scraper.Parameters, progress: Progress) -> List[Article]:
        response = requests.get(self._URL)
        response.raise_for_status()
        html = response.text

        soup = BeautifulSoup(html, "html.parser")

        body_text = soup.find("div", class_="bodyText")
        assert body_text

        h2 = body_text.find("h2", string="Pressemitteilungen")  # type: ignore
        assert h2

        entries = []
        for tag in h2.next_siblings:
            if not isinstance(tag, Tag):
                continue
            if tag.name == "p":
                a = tag.find("a")
                assert a
                text = a.get_text()
                date_str, title_str = text.split(":")

                day, month, year = date_str.strip().split(" ")
                day = int(day.strip("."))
                month = self._GERMAN_MONTHS.index(month.strip())
                year = int(year.strip())
                timestamp = datetime(day=day, month=month, year=year)

                title = title_str.strip()

                link = str(a["href"])

                entries.append((title, link, timestamp))

            else:
                break

        articles = []
        for title, link, timestamp in progress.start_iteration(entries, total=len(entries), desc="Scraping DSC articles"):
            response = requests.get(link)
            response.raise_for_status()
            html = response.text
            soup = BeautifulSoup(html, "html.parser")

            div = soup.find("div", class_="wrapperText")
            assert div

            ps = div.find_all("p", class_=False)
            assert ps
            content = "\n\n".join(p.text.strip() for p in ps)

            articles.append(Article(
                timestamp=timestamp,
                title=title,
                content=content,
                link=link, 
                source=self.SOURCE
            ))

        return self._filter_dates(articles, parameters)

    _URL_PREFIX: str = "https://www.dsc.bund.de/"
    _URL: str = f"{_URL_PREFIX}DSC/DE/Aktuelles/start.html"
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
