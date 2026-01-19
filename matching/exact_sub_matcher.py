from __future__ import annotations
from matching.sub_matcher import SubMatcher
from dataclasses import dataclass
from typing import List


class ExactSubMatcher(SubMatcher):

    @dataclass
    class Parameters(SubMatcher.Parameters):
        pass

    @dataclass
    class Result(SubMatcher.Result):

        def filter_by_mask(self, mask: List[bool]) -> "SubMatcher.Result":
            """Default implementation: filter the outer list (texts)."""
            filtered_matches = [row for row, keep in zip(self.matches, mask) if keep]
            return type(self)(filtered_matches)  # works for simple results

    def match(self, keywords: List[str], texts: List[str], parameters: Parameters) -> Result:  # type: ignore
        lower_keywords = [keyword.lower() for keyword in keywords]
        lower_texts = [text.lower() for text in texts]
        
        matches = []
        for lower_text in lower_texts:
            matches.append([])
            for lower_keyword in lower_keywords:
                matches[-1].append(lower_keyword.lower() in lower_text.lower())
        return ExactSubMatcher.Result(matches)
        