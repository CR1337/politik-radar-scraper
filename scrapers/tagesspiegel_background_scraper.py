from typing import List
from article import Article
from scrapers.scraper import Scraper
from dataclasses import dataclass
from datetime import datetime
from bs4 import BeautifulSoup
from progress import Progress
import streamlit as st

class TagesspiegelBackgroundScraper(Scraper):

    SOURCE: str = "Tagesspiegel Background"

    @dataclass
    class Parameters(Scraper.Parameters):
        pass

    def scrape(
        self, parameters: Scraper.Parameters, progress: Progress
    ) -> List[Article]:
        articles = []
        if st.session_state["uploaded_files"]:
            for uploaded_file in st.session_state["uploaded_files"]:
                soup = BeautifulSoup(uploaded_file, "html.parser")


                titles = soup.find_all("h2",{"style":"font-size:22px; font-family: AbrilText-SemiBold, Georgia, serif; line-height:31px; font-weight: bold; margin: 0; padding:0; color:#2a2a2a;"})
                contents = [title.find_next("p") for title in titles]
                date_str = soup.find("td",{"style":"font-family: FranklinGothic-Book, Helvetica, Arial, sans-serif; font-size:14px; line-height: 18px; color:#fff;"})
                date_without_briefing = date_str.get_text(strip=True).replace("Briefing ", "")
                date_obj = datetime.strptime(date_without_briefing, "%d.%m.%Y")

                for i in progress.start_iteration(
                    range(len(contents)), total=len(contents), desc="Scraping Tagesspiegel Background entries"
                ):
                    if contents[i]:
                        articles.append(
                            Article(
                                timestamp=date_obj,
                                title=titles[i].get_text(),
                                medium_organisation=self.SOURCE,
                                content=contents[i].get_text(),
                                link="",
                                source=self.SOURCE,
                            )
                        )

        return self._filter_dates(articles, parameters)


    
