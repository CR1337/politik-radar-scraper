from typing import Dict, List
from article import Article
from scrapers.scraper import Scraper
from dataclasses import dataclass
from datetime import datetime
from bs4 import BeautifulSoup 
from progress import Progress


class HibScraper(Scraper):

    SOURCE: str = "Heute im Bundestag"

    @dataclass
    class Parameters(Scraper.Parameters):
        pass

    def scrape(self, parameters: Scraper.Parameters, progress: Progress) -> List[Article]:
        entry_parameters = self._EntryParameters(
            start_date=parameters.start_date,
            end_date=parameters.end_date,
            offset=0,
            limit=self._LIMIT
        )
        entries = self._scrape_entries(entry_parameters, progress)
        articles = self._scrape_articles(entries, progress)
        articles = self._filter_dates(articles, parameters)

        articles = list(set(articles))

        return articles

    _LIMIT: int = 20
    _MS_PER_S: int = 1_000
    _URL: str = "https://www.bundestag.de/ajax/filterlist/de/presse/hib/454590-454590"
    _ARCIVE_URL: str = "https://www.bundestag.de/ajax/filterlist/webarchiv/presse/hib/867560-867560"
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

    @dataclass
    class _EntryParameters:
        start_date: datetime
        end_date: datetime
        offset: int
        limit: int

        no_filter_set: bool = False
        start_field: str = "date"
        end_field: str = "date"

        def to_dict(self) -> Dict[str, str]:
            return {
                "startdate": str(int(self.start_date.timestamp() * HibScraper._MS_PER_S)),
                "enddate": str(int(self.end_date.timestamp() * HibScraper._MS_PER_S)),
                "offset": str(self.offset),
                "limit": str(self.limit),
                "noFilterSet": str(self.no_filter_set).lower(),
                "startfield": self.start_field,
                "endfield": self.end_field
            }

    @dataclass
    class _Entry:
        title: str
        url: str
        timestamp: datetime
    
    def _scrape_entries_with_url(self, url: str, parameters: _EntryParameters, progress: Progress) -> List[_Entry]:
        entry_length = -1
        n_iterations = 0
        entries = []
        parameters.offset = 0

        while entry_length != len(entries):
            entry_length = len(entries)
            parameters.offset = n_iterations * self._LIMIT

            html = self._get(self._URL, progress, f"Fehler beim Scrapen der Quelle: {self.SOURCE}", parameters=parameters.to_dict())
            if html is None:
                return []

            soup = BeautifulSoup(html, "html.parser")
            containers = soup.find_all("div", class_="bt-listenteaser")
            if not containers:
                break

            items = []
            for container in containers:
                items.extend(container.select("ul.bt-linkliste li"))

            for li in items:
                a_tag = li.find("a", class_="bt-link-intern")
                assert a_tag is not None
                title = a_tag.get_text(strip=True)

                url = a_tag["href"]

                h4_tag = li.find_previous("h4")
                assert h4_tag is not None
                date_str = h4_tag.get_text(strip=True)

                day, month, year = date_str.split(" ")
                day = int(day[:-1])
                month = self._GERMAN_MONTHS.index(month)
                year = int(year)

                timestamp = datetime(year=year, month=month, day=day)

                entries.append(self._Entry(title, url, timestamp))

            n_iterations += 1

        return entries

    def _scrape_entries(self, parameters: _EntryParameters, progress: Progress) -> List[_Entry]:
        entries = self._scrape_entries_with_url(self._URL, parameters, progress)
        entries.extend(self._scrape_entries_with_url(self._ARCIVE_URL, parameters, progress))
        return entries

    def _scrape_articles(self, entries: List[_Entry], progress: Progress) -> List[Article]:
        articles = []
        for entry in progress.start_iteration(entries, total=len(entries), desc="Scraping 'Heute im Bundestag' Artikel"):
            html = self._get(entry.url, progress, f"Fehler beim Scrapen der Quelle: {self.SOURCE} bei Artikel {entry.title}")
            if html is None:
                return []

            soup = BeautifulSoup(html, "html.parser")
            article_div=soup.find("div", class_="bt-artikel__article")
            assert article_div is not None
            content = self._content_to_markdown(article_div).strip()
            content = content.split("\n")[0]

            header_line = soup.find("span", class_="bt-dachzeile")
            assert header_line is not None
            header_string = header_line.text
            medium_organisation = header_string.split("—")[0].strip().split(" ")[0].strip().replace(",", "")

            articles.append(Article(
                timestamp=entry.timestamp,
                title=entry.title,
                medium_organisation=medium_organisation,
                content=content,
                link=entry.url,
                source=self.SOURCE
            ))

        return articles
       