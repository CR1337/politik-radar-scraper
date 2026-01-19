from __future__ import annotations
from matching.sub_matcher import SubMatcher
from dataclasses import dataclass
from typing import List
from nltk.stem import SnowballStemmer
from nltk import word_tokenize


class StemSubMatcher(SubMatcher):

    @dataclass
    class Parameters(SubMatcher.Parameters):
        pass

    @dataclass
    class Result(SubMatcher.Result):

        def filter_by_mask(self, mask: List[bool]) -> "SubMatcher.Result":
            """Default implementation: filter the outer list (texts)."""
            filtered_matches = [row for row, keep in zip(self.matches, mask) if keep]
            return type(self)(filtered_matches)  # works for simple results
        
    _LANGUAGE: str = "german"
    _STEMMER: SnowballStemmer = SnowballStemmer(_LANGUAGE)

    def match(self, keywords: List[str], texts: List[str], parameters: Parameters) -> Result:  # type: ignore
        keyword_stems = [
            self._STEMMER.stem(keyword).lower()
            for keyword in keywords
        ]
        text_stems = [
            " ".join(
                self._STEMMER.stem(token).lower()
                for token in word_tokenize(text, language=self._LANGUAGE)
            )
            for text in texts
        ]
        
        matches = []
        for text_stem in text_stems:
            matches.append([])
            for keyword_stem in keyword_stems:
                matches[-1].append(keyword_stem in text_stem)
        return StemSubMatcher.Result(matches)
        