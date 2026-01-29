from typing import List
from article import Article
from scrapers.scraper import Scraper
from dataclasses import dataclass
from datetime import datetime
from bs4 import BeautifulSoup 
from progress import Progress


class BvaScraper(Scraper):

    SOURCE: str = "BVA"

    @dataclass
    class Parameters(Scraper.Parameters):
        pass

    def scrape(self, parameters: Scraper.Parameters, progress: Progress) -> List[Article]:
        html = self._get(self._URL, progress, f"Fehler beim Scrapen der Quelle: {self.SOURCE}")
        if html is None:
            return []

        soup = BeautifulSoup(html, "html.parser")

        lis = soup.find_all("li", class_="c-searchteaser")

        articles = []
        for li in progress.start_iteration(lis, total=len(lis), desc="Scraping BVA entries"):
            title_a = li.find("a", class_="c-searchteaser__l")
            content_p = li.find("p", class_="c-searchteaser__p")
            date_p = li.find("p", class_="c-searchteaser__small")

            assert title_a
            assert content_p
            assert date_p

            link = str(title_a["href"])
            title = title_a.text
            content = content_p.text.strip()

            day, month, year = (int(s) for s in date_p.text.split("|")[0].strip().split("."))

            articles.append(Article(
                datetime(year=year, month=month, day=day),
                title=title,
                medium_organisation=self.SOURCE,
                content=content,
                link=link, 
                source=self.SOURCE
            ))

        return self._filter_dates(articles, parameters)

    _URL_PREFIX: str = "https://www.bva.bund.de/"
    _URL: str = f"{_URL_PREFIX}SiteGlobals/Forms/Suche/Expertensuche/Expertensuche_Formular.html?documentType_=pressrelease&sortOrder=dateOfIssue_dt+desc"
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
