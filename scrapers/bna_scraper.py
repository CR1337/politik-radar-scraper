from typing import List
from article import Article
from scrapers.scraper import Scraper
from dataclasses import dataclass
from datetime import datetime
from bs4 import BeautifulSoup 
from bs4.element import Tag
from progress import Progress


class BnaScraper(Scraper):

    SOURCE: str = "BNA"

    @dataclass
    class Parameters(Scraper.Parameters):
        pass

    def scrape(self, parameters: Scraper.Parameters, progress: Progress) -> List[Article]:
        html = self._get(self._URL, progress, f"Fehler beim Scrapen der Quelle: {self.SOURCE}")
        if html is None:
            return []

        soup = BeautifulSoup(html, "html.parser")

        table = soup.find("table", class_="textualData links")
        assert table
        tbody = table.find("tbody")
        assert tbody

        trs = tbody.find_all("tr")
        
        articles = []
        for tr in progress.start_iteration(trs, len(trs), "Scraping BNA articles..."):
            tds = tr.find_all("td")
            assert len(tds) == 2

            date_td, rest_td = tds

            day, month, year = (int(x) for x in date_td.text.split("."))
            timestamp = datetime(day=day, month=month, year=year)

            a = rest_td.find("a", class_="titleLink")
            assert a

            link = self._URL_PREFIX + a.get("href")
            title = a.text

            sub_html = self._get(link, progress, f"Fehler beim Scrapen der Quelle: {self.SOURCE} bei Artikel: {title}")
            if sub_html is None:
                return []

            sub_soup = BeautifulSoup(sub_html, "html.parser")

            wrapper_div = sub_soup.find("div", class_="wrapperText")
            assert wrapper_div

            ps = wrapper_div.find_all("p")
            assert len(ps) > 1
            no_class_ps = [p for p in ps if not p.has_attr("class")]
            assert len(no_class_ps) > 0

            content = no_class_ps[0].text

            articles.append(Article(
                timestamp=timestamp,
                title=title,
                medium_organisation=self.SOURCE,
                content=content,
                link=link, 
                source=self.SOURCE
            ))

        return self._filter_dates(articles, parameters)


    _URL_PREFIX: str = "https://www.bundesnetzagentur.de/"
    _URL: str = f"{_URL_PREFIX}DE/Allgemeines/Presse/Pressemitteilungen/start.html"
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
