from typing import List
from article import Article
from scrapers.scraper import Scraper
from dataclasses import dataclass
from datetime import datetime
from bs4 import BeautifulSoup 
from bs4.element import Tag
from progress import Progress


class BsiScraper(Scraper):

    SOURCE: str = "BSI"

    @dataclass
    class Parameters(Scraper.Parameters):
        pass

    def scrape(self, parameters: Scraper.Parameters, progress: Progress) -> List[Article]:
        html = self._get(self._URL, progress, f"Fehler beim Scrapen der Quelle: {self.SOURCE}")
        if html is None:
            return []

        soup = BeautifulSoup(html, "html.parser")

        search_results_lis = soup.find_all("li", class_="c-search-result-teaser")

        articles = []
        for li in progress.start_iteration(search_results_lis, total=len(search_results_lis), desc="Scraping BSI articles"):
            timestamp_tag = li.find("time", class_="c-search-result-teaser__date")
            assert timestamp_tag
            timestamp_string = str(timestamp_tag.get("datetime"))
            year, month, day = (int(x) for x in timestamp_string.split("-"))
            timestamp = datetime(day=day, month=month, year=year)

            title_h4 = li.find("h4", class_="c-search-result-teaser__headline")
            assert title_h4
            title = title_h4.text

            content_div = li.find("div", class_="c-search-result-teaser__content")
            assert content_div
            content_p = content_div.find("p")
            assert content_p
            content = content_p.text

            link_a = li.find("a", class_="c-search-result-teaser__link")
            assert link_a
            link = self._URL_PREFIX + str(link_a.get("href"))

            articles.append(Article(
                timestamp=timestamp,
                title=title,
                medium_organisation=self.SOURCE,
                content=content,
                link=link, 
                source=self.SOURCE
            ))

        return self._filter_dates(articles, parameters)


    _URL_PREFIX: str = "https://www.bsi.bund.de/"
    _URL: str = f"{_URL_PREFIX}/SiteGlobals/Forms/Suche/Expertensuche_Pressemitteilungen_Formular.html"
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
