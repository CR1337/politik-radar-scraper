from typing import List
from article import Article
from scrapers.scraper import Scraper
from dataclasses import dataclass
from datetime import datetime
from bs4 import BeautifulSoup 
from bs4.element import Tag
from progress import Progress


class BmiScraper(Scraper):

    SOURCE: str = "BMI"

    @dataclass
    class Parameters(Scraper.Parameters):
        pass

    def scrape(self, parameters: Scraper.Parameters, progress: Progress) -> List[Article]:
        html = self._get(self._URL, progress, f"Fehler beim Scrapen der Quelle: {self.SOURCE}")
        if html is None:
            return []

        soup = BeautifulSoup(html, "html.parser")

        ol = soup.find("ol", class_="c-search-teaser__ol")
        assert ol
        lis = list(ol.find_all("li", class_="c-search-teaser__li"))[:-1]

        articles = []
        for li in progress.start_iteration(lis, len(lis), "Scraping BMI articles..."):
            type_span = li.find("span", class_="c-search-teaser__span c-search-teaser__type")
            assert type_span
            type_string = str(type_span.text).lower()
            if type_string == "download":
                continue

            a = li.find("a", class_="c-search-teaser__true-link")
            assert a
            link = self._URL_PREFIX + a.get("href")

            title_span = a.find("span", class_="c-search-teaser__headline")
            assert title_span
            title = str(title_span.text).strip()

            date_span = li.find("span", class_="c-search-teaser__span c-search-teaser__date")
            assert date_span
            date_string = date_span.text
            day, month, year = [int(x) for x in date_string.split(".")]
            timestamp = datetime(day=day, month=month, year=year)

            sub_html = self._get(link, progress, f"Fehler beim Scrapen der Quelle: {self.SOURCE} bei Artikel: {title}")
            if sub_html is None:
                return []

            sub_soup = BeautifulSoup(sub_html, "html.parser")

            content_div = sub_soup.find("div", class_="c-content-article")
            assert content_div
            content_ps = content_div.find_all("p", class_=False, recursive=False)
            content_p = None
            for p in content_ps:
                if len(p.text) > 0:
                    if p.find("aside"):
                        continue
                    content_p = p
                    break
            assert content_p
            content = self._content_to_markdown(content_p).strip()
            print(f"{title=}", flush=True)
            print(f"{content=}", flush=True)

            articles.append(Article(
                timestamp=timestamp,
                title=title,
                medium_organisation=self.SOURCE,
                content=content,
                link=link, 
                source=self.SOURCE
            ))

        return self._filter_dates(articles, parameters)

    _URL_PREFIX: str = "https://www.bmi.bund.de/"
    _URL: str = f"{_URL_PREFIX}SiteGlobals/Forms/suche/expertensuche-formular.html"
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
