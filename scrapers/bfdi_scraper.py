from typing import List
from article import Article
from scrapers.scraper import Scraper
from dataclasses import dataclass
from datetime import datetime
from progress import Progress
from bs4 import BeautifulSoup 


class BfdiScraper(Scraper):

    SOURCE: str = "BfDI"

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

        rows = table.find_all("tr")
        assert rows

        entries = []
        for row in rows[1:]:
            date_td = row.find("td")
            assert date_td

            title_link_td = date_td.find_next_sibling("td")
            assert title_link_td
            title_link_a = title_link_td.find("a")
            assert title_link_a

            day, month, year = (int(x) for x in date_td.text.split("."))
            timestamp = datetime(year=year, month=month, day=day)

            title = str(title_link_a["title"])
            link = f"{self._URL_PREFIX}{str(title_link_a['href'])}"

            entries.append((timestamp, title, link))

        articles = []
        for timestamp, title, link in progress.start_iteration(entries, total=len(entries), desc="Scraping BfDI articles"):
            html = self._get(link, progress, f"Fehler beim Scrapen der Quelle: {self.SOURCE} bei Artikel: {title}")
            if html is None:
                continue
        
            soup = BeautifulSoup(html, "html.parser")

            main = soup.find("main", class_="main row")
            assert main

            ps = main.find_all("p")
            assert ps

            content = "\n\n".join([p.text for p in ps][:2])

            articles.append(Article(
                timestamp=timestamp,
                title=title,
                medium_organisation=self.SOURCE,
                content=content,
                link=link,
                source=self.SOURCE
            ))

        return self._filter_dates(articles, parameters)


    _URL_PREFIX: str = "https://www.bfdi.bund.de/"
    _URL: str = f"{_URL_PREFIX}/DE/BfDI/Presse/Pressemitteilungen/pressemitteilungen_node.html"
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
