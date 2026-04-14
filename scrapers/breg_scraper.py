from typing import List
from article import Article
from scrapers.scraper import Scraper
from dataclasses import dataclass
from datetime import datetime
from progress import Progress
from bs4 import BeautifulSoup
import re
import json
import html as HTML


class BregScraper(Scraper):

    SOURCE: str = "BREG"

    @dataclass
    class Parameters(Scraper.Parameters):
        pass

    def scrape(
        self, parameters: Scraper.Parameters, progress: Progress
    ) -> List[Article]:
        page = 1
        entries = []
        while (
            page < 10
        ):  # gerade weil es sonst einfach zu lange dauert. TODO: andere Möglichkeit finden
            url_page = f"{self._URL}?page={page}"
            html_text = self._get(
                url_page, progress, f"Fehler beim Scrapen der Quelle: {self.SOURCE}"
            )
            assert html_text

            soup = BeautifulSoup(html_text, "html.parser")
            scripts = soup.find_all("script")
            data = None
            for script in scripts:
                if script.string and "BPA.initialSearchResultsJson" in script.string:
                    match = re.search(
                        r"BPA\.initialSearchResultsJson\s*=\s*(\{.*?\});",
                        script.string,
                        re.DOTALL,
                    )
                    if match:
                        json_str = match.group(1)
                        data = json.loads(json_str)
                        break
            if not data or not data["result"]:
                print("Keine weiteren Ergebnisse.")
                break
            data = data["result"]["items"]
            for item in data:
                timestamp = datetime.fromisoformat(item["sortDate"])
                payload = HTML.unescape(item["payload"])
                soup_payload = BeautifulSoup(payload, "html.parser")
                a_tag = soup_payload.find("a", class_="bpa-link")
                assert a_tag
                link = a_tag["href"] if a_tag else None

                title_tag = soup_payload.find(
                    "span", class_="bpa-teaser-title-text-inner"
                )
                assert title_tag
                title = title_tag.get_text(strip=True)

                if not (
                    title.startswith("Bundeskabinett - Ergebnisse")
                    or title.startswith("Regierungspressekonferenz")
                ):
                    entries.append((timestamp, title, link))
            page += 1

        articles = []
        for timestamp, title, link in progress.start_iteration(
            entries, total=len(entries), desc="Scraping Breg articles"
        ):
            html = self._get(
                link,
                progress,
                f"Fehler beim Scrapen der Quelle: {self.SOURCE} bei Artikel: {title}",
            )
            if html is None:
                continue

            soup = BeautifulSoup(html, "html.parser")

            main = soup.find("main")
            if main:
                ps = main.find_all("p")
                content = "\n\n".join([p.text for p in ps])

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

    _URL_PREFIX: str = "https://www.bundesregierung.de/"
    _URL: str = f"{_URL_PREFIX}/breg-de/aktuelles"
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
