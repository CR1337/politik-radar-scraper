from typing import List
from article import Article
from scrapers.scraper import Scraper
from dataclasses import dataclass
from datetime import datetime
from bs4 import BeautifulSoup
from progress import Progress


class BmjvScraper(Scraper):

    SOURCE: str = "BMJV"

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

        urls = soup.find_all("a", {"class": "c-teaser__link-main"})
        articles = []
        for url in progress.start_iteration(
            urls, len(urls), "Scraping bmjv articles..."
        ):
            link = f"{self._URL_PREFIX}{url.get('href')}"
            html_article = self._get(
                link, progress, f"Fehler beim Scrapen der Quelle: {self.SOURCE}"
            )
            assert html_article
            soup = BeautifulSoup(html_article, "html.parser")
            h1 = soup.find("h1", class_="c-page-intro__headline")
            assert h1
            title = h1.get_text(strip=True)
            main = soup.find("div", class_="small-12 medium-8 medium-offset-2 column")

            if main:
                ps = main.find_all("p")
                content = "\n\n".join([p.text for p in ps])
                time_tag = soup.find("time")
                assert time_tag
                datetime_string = time_tag.get("datetime")
                assert isinstance(datetime_string, str)
                timestamp = datetime.fromisoformat(datetime_string)
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

    _URL_PREFIX: str = "https://www.bmjv.de/"
    _URL: str = (
        f"{_URL_PREFIX}SiteGlobals/Forms/AlleMeldungen/allemeldungen_Formular.html?nn=17116&folderInclude.HASH=f5491235196717d2fa4ae392487b1b2ed84c4b00fda7&folderExclude=-%2FBMJ%2F*%2FRestricted+-%2FBMJ%2FSharedDocs%2FDownloads%2F*+-%2FBMJ%2FSharedDocs%2FPublikationen%2FDE%2FBroschueren_Sprachvarianten%2F*+-%2FBMJ%2F_doc%2F*++-%2FBMJ%2FSharedDocs%2FPublikationen%2FDE%2FSortieren_Fachpublikationen%2F*&callerId.HASH=0b341aafcef276922cefa276b44edfd226a147da8583&folderExclude.HASH=c12cfd8c3f85d46cb5ef7d6092312a7cef393133d920&folderInclude=%2FBMJ%2FSharedDocs%2FPressearchiv%2F*+%2FBMJ%2FSharedDocs%2FInterviews%2FDE%2F*+%2FBMJ%2FSharedDocs%2FPressemitteilungen%2FDE%2F*+%2FBMJ%2FSharedDocs%2FZitate%2FDE%2F*+%2FBMJ%2FSharedDocs%2FKurzmeldungen%2FDE%2F*+%2FBMJ%2FSharedDocs%2FMeldungen%2FDE%2F*&callerId=148026"
    )

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
