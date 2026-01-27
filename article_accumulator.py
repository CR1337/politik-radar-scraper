from matching.match_filter import MatchFilter
import pandas as pd
from typing import List, Tuple
import numpy as np


class ArticleAccumulator:
    
    def to_dataframe(self, filter_result: MatchFilter.Result, keywords: List[str], add_results: bool) -> Tuple[pd.DataFrame, List[str]]:
        articles = filter_result.articles
        m = filter_result.matcher_result

        # Base dataframe with article fields
        df: pd.DataFrame = pd.DataFrame([{
            "__SORTER__": a.timestamp,
            "timestamp": a.timestamp.strftime("%d.%m.%Y"),
            "title": a.title,
            "medium_organisation": a.medium_organisation,
            "content": a.content,
            "link": a.link,
            "source": a.source
        } for a in articles])

        if len(df):
            df = df.sort_values(by="timestamp")

        df = df.drop("__SORTER__", axis=1)

        if not add_results:
            return df, []

        # Helper to fetch a match matrix (keywords × articles)
        # If a submatcher is disabled: return all False
        def get_match_matrix(sub_result, n_keywords, n_articles):
            if sub_result is None:
                return np.zeros((n_keywords, n_articles), dtype=bool)
            return np.array(sub_result.matches)

        n_keywords = len(keywords)
        n_articles = len(articles)

        # Extract match matrices
        exact_matches      = get_match_matrix(m.exact_result,     n_keywords, n_articles)
        stem_matches       = get_match_matrix(m.stem_result,      n_keywords, n_articles)
        similarity_matches = get_match_matrix(m.similarity_result,n_keywords, n_articles)

        # Similarities: if embedding off -> zeros
        if m.similarity_result is None:
            cosine_sims = np.zeros((n_keywords, n_articles), dtype=float)
        else:
            # m.embedding_result.cosine_similarities is (kw × text)
            cosine_sims = np.array(m.similarity_result.cosine_similarities)

        # Initialize a dictionary to hold all new columns
        new_columns = {}
        bool_columns = []

        for kw_idx, kw in enumerate(keywords):
            prefix = f"{kw}"

            if filter_result.matcher_result.exact_result is not None:
                new_columns[f"{prefix} - exact match"] = exact_matches[:, kw_idx]
                bool_columns.append(f"{prefix} - exact match")
            if filter_result.matcher_result.stem_result is not None:
                new_columns[f"{prefix} - stem match"] = stem_matches[:, kw_idx]
                bool_columns.append(f"{prefix} - stem match")
            if filter_result.matcher_result.similarity_result is not None:
                new_columns[f"{prefix} - similarity match"] = similarity_matches[:, kw_idx]
                new_columns[f"{prefix} - similarity"] = cosine_sims[:, kw_idx]
                bool_columns.append(f"{prefix} - similarity match")

        # Concatenate all new columns at once
        df = pd.concat([df, pd.DataFrame(new_columns)], axis=1)

        df = df[df[bool_columns].any(axis=1)]

        return df, bool_columns
    