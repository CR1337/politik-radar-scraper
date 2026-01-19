from __future__ import annotations
from matching.sub_matcher import SubMatcher
from dataclasses import dataclass
from typing import List, Set
from nltk.stem import SnowballStemmer
from stemmer import Stemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import json


class SimilaritySubMatcher(SubMatcher):

    @dataclass
    class Parameters(SubMatcher.Parameters):
        cosine_threshold: float

    @dataclass
    class Result(SubMatcher.Result):
        cosine_similarities: np.ndarray

        def filter_by_mask(self, mask: List[bool]) -> "SubMatcher.Result":
            idx = np.array(mask)
            return SimilaritySubMatcher.Result(
                matches=[row for row, keep in zip(self.matches, mask) if keep],
                cosine_similarities=self.cosine_similarities[idx]
            )

    _LANGUAGE: str = "german"
    _STEMMER: SnowballStemmer = SnowballStemmer(_LANGUAGE)
    with open("german_stopwords.json", 'r') as file:
        _STOPWORDS: Set[str] = set(json.load(file))

    def match(self, keywords: List[str], texts: List[str], parameters: Parameters) -> Result:  # type: ignore
        keyword_stems = [Stemmer.stem(keyword) for keyword in keywords]
        text_stems = [Stemmer.stem(text) for text in texts]
        
        vectorizer = TfidfVectorizer(stop_words=list(self._STOPWORDS))
        tfidf_matrix = vectorizer.fit_transform(text_stems)
        query_matrix = vectorizer.transform(keyword_stems)

        cosine_similarities = np.sqrt(cosine_similarity(tfidf_matrix, query_matrix))

        matches = []
        for text_idx in range(len(text_stems)):
            matches.append([])
            for keyword_idx in range(len(keyword_stems)):
                matches[-1].append(float(cosine_similarities[text_idx][keyword_idx]) >= parameters.cosine_threshold)

        return SimilaritySubMatcher.Result(
            matches,
            cosine_similarities
        )
    