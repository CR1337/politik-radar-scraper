from article import Article
from bs4 import BeautifulSoup
from progress import Progress
from dateutil import parser
import feedparser


def scrape_rss(URL, source, datestring, progress: Progress):
    feed = feedparser.parse(URL)
    articles = []
    if feed and hasattr(feed, "entries"):
        for entry in progress.start_iteration(
            feed.entries, len(feed.entries), f"Scraping {source}..."
        ):
            soup = BeautifulSoup(entry.description, "html.parser")
            content = soup.get_text()
            try:
                source_res = entry.source["title"]
            except (AttributeError, KeyError):
                source_res = source
            articles.append(
                Article(
                    timestamp=parser.parse(entry.published),
                    title=entry.title,
                    medium_organisation=source,
                    content=content,
                    link=entry.link,
                    source=source_res,
                )
            )

    return articles
