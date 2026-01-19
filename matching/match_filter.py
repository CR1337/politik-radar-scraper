from typing import List
from article import Article
from matching.matcher import Matcher
from dataclasses import dataclass
from progress import Progress


class MatchFilter:

    @dataclass
    class Result:
        articles: List[Article]
        matcher_result: Matcher.Result

        @classmethod
        def empty(cls) -> "MatchFilter.Result":
            return cls([], Matcher.Result())

    def filter_articles(self, articles: List[Article], matcher_result: Matcher.Result, keywords: List[str], progress: Progress) -> Result:
        match_mask = matcher_result.match_mask(len(articles), len(keywords))
        
        filtered_articles = []
        for mask, article in progress.start_iteration(zip(match_mask, articles), len(articles), "Filtering"):
            if mask:
                filtered_articles.append(article)

        filtered_matcher_result = matcher_result.filter_self(len(articles), len(keywords))

        return MatchFilter.Result(filtered_articles, filtered_matcher_result)
        