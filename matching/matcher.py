from matching.sub_matcher import SubMatcher
from matching.exact_sub_matcher import ExactSubMatcher
from matching.stem_sub_matcher import StemSubMatcher
from matching.similarity_sub_matcher import SimilaritySubMatcher
from typing import Dict, List, Set, Optional
from enum import Enum
from dataclasses import dataclass
import numpy as np
from article import Article
from progress import Progress


class SubMatcherType(Enum):
    EXACT = "exact"
    STEM = "stem"
    LEMMA = "lemma"
    EMBEDDING = "embedding"
    SIMILARITY = "similarity"
    ALL = "all"


class Matcher:

    @dataclass
    class Parameters:
        sub_matcher_selection: Set[SubMatcherType]

        exact_parameters: Optional[ExactSubMatcher.Parameters] = None
        stem_parameters: Optional[StemSubMatcher.Parameters] = None
        similarity_parameters: Optional[SimilaritySubMatcher.Parameters] = None

    @dataclass
    class FilterResult:
        articles: List[Article]
        matcher_result: "Matcher.Result"

    @dataclass
    class Result:
        exact_result: Optional[ExactSubMatcher.Result] = None
        stem_result: Optional[StemSubMatcher.Result] = None
        similarity_result: Optional[SimilaritySubMatcher.Result] = None

        def all_results(self, n_texts: int, n_keywords: int) -> List[SubMatcher.Result]:
            return [
                self.exact_result or ExactSubMatcher.Result(
                    [[False for _0 in range(n_keywords)] for _1 in range(n_texts)]
                ),
                self.stem_result or StemSubMatcher.Result(
                    [[False for _0 in range(n_keywords)] for _1 in range(n_texts)]
                ),
                self.similarity_result or SimilaritySubMatcher.Result(
                    [[False for _0 in range(n_keywords) for _1 in range(n_texts)]],
                    np.empty(shape=(n_texts, n_keywords))
                )
            ]
        
        def match_mask(self, n_texts: int, n_keywords: int) -> List[bool]:
            results = self.all_results(n_texts, n_keywords)

            return [
                any(result.matches[text_idx][keyword_idx]
                    for result in results
                    for keyword_idx in range(n_keywords))
                for text_idx in range(n_texts)
            ]
        
        def filter_self(self, n_texts: int, n_keywords: int) -> "Matcher.Result":
            match_mask = self.match_mask(n_texts, n_keywords)
            return Matcher.Result(
                exact_result=self.exact_result.filter_by_mask(match_mask)  # type: ignore
                    if self.exact_result else None,

                stem_result=self.stem_result.filter_by_mask(match_mask)  # type: ignore
                    if self.stem_result else None,

                similarity_result=self.similarity_result.filter_by_mask(match_mask)  # type: ignore
                    if self.similarity_result else None,
            )
    
    _SUB_MATCHERS: Dict[str, SubMatcher] = {
        "exact": ExactSubMatcher(),
        "stem": StemSubMatcher(),
        "similarity": SimilaritySubMatcher(),
    }

    def match(self, parameters: Parameters, keywords: List[str], texts: List[str], progress: Progress) -> Result:
        result = self.Result()

        for sub_matcher_key, sub_matcher in progress.start_iteration(self._SUB_MATCHERS.items(), len(self._SUB_MATCHERS.items()), desc="Matching"):
            if SubMatcherType(sub_matcher_key) in parameters.sub_matcher_selection:
                sub_matcher_parameters = getattr(parameters, f"{sub_matcher_key}_parameters")
                assert sub_matcher_parameters is not None
                sub_matcher_result = sub_matcher.match(keywords, texts, sub_matcher_parameters)
                setattr(result, f"{sub_matcher_key}_result", sub_matcher_result)

        return result
