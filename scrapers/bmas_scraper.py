from typing import List
from article import Article
from scrapers.scraper import Scraper
from dataclasses import dataclass
from datetime import datetime
from bs4 import BeautifulSoup 
from bs4.element import Tag
from progress import Progress


class BmasScraper(Scraper):

    SOURCE: str = "BMAS"

    @dataclass
    class Parameters(Scraper.Parameters):
        pass

    def scrape(self, parameters: Scraper.Parameters, progress: Progress) -> List[Article]:
        html = self._get(self._URL, progress, f"Fehler beim Scrapen der Quelle: {self.SOURCE}")
        if html is None:
            return []

        soup = BeautifulSoup(html, "html.parser")

        pp_list = soup.find("pp-list", attrs={"direction": "column", "ordered-list": "true", "grid": "true", "columns": "1", "data-slot": "pp-list"})
        assert pp_list
        pp_teasers = pp_list.find_all("pp-teaser", attrs={"data-slot": "pp-teaser"})

        articles = []
        for pp_teaser in progress.start_iteration(pp_teasers, len(pp_teasers), "Scraping BMAS articles..."):
            pp_link = pp_teaser.find("pp-link")
            assert pp_link
            link = pp_link.get("href")

            title_h3 = pp_link.find("h3")
            assert title_h3
            title = self._content_to_markdown(title_h3).replace("\n", "")

            date_time = pp_teaser.find("time")
            assert date_time
            date_string = date_time.get("datetime")
            year, month, day = [int(x) for x in date_string.split("-")]
            timestamp = datetime(day=day, month=month, year=year)

            content_p = pp_teaser.find("p", class_="text")
            assert content_p
            content = str(content_p.text).strip()

            articles.append(Article(
                timestamp=timestamp,
                title=title,
                medium_organisation=self.SOURCE,
                content=content,
                link=link, 
                source=self.SOURCE
            ))

        return self._filter_dates(articles, parameters)

    _URL_PREFIX: str = "https://www.bmas.de"
    _URL: str = f"{_URL_PREFIX}/SiteGlobals/Forms/Suche/Aktuelles-Suche_Formular.html?showNoStatus.HASH=ee44dc062ff16b7110f&showNoGesetzesstatus=true&showNoStatus=true&showNoGesetzesstatus.HASH=7489c1329448b770d3b8&documentType_="
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
