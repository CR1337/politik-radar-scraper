from matching.match_filter import MatchFilter
import pandas as pd
from io import StringIO, BytesIO
from typing import List, Optional
import numpy as np
from datetime import datetime
from dataclasses import dataclass


class ArticleSerializer:

    @dataclass
    class Metadata:
        timestamp: datetime
        keywords: List[str]
        cos_threshold: Optional[float] = None

        def __str__(self) -> str:
            return f"""
# Abrufzeitpunkt: {self.timestamp.isoformat()}
# Schlagworte: {', '.join(self.keywords)}
# Ähnlichkeitsgrenzwert: {self.cos_threshold or 'NA'}
""".strip()
    
    def to_dataframe(self, filter_result: MatchFilter.Result, keywords: List[str], add_results: bool) -> pd.DataFrame:
        articles = filter_result.articles
        m = filter_result.matcher_result

        # Base dataframe with article fields
        df = pd.DataFrame([{
            "timestamp": a.timestamp,
            "title": a.title,
            "content": a.content,
            "link": a.link,
            "source": a.source
        } for a in articles])

        if len(df):
            df = df.sort_values(by="timestamp")

        if not add_results:
            return df

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

        # Now create columns for each keyword
        # for kw_idx, kw in enumerate(keywords):
        #     prefix = f"{kw}"

        #     if filter_result.matcher_result.exact_result is not None:
        #         df[f"{prefix} - exact match"]     = exact_matches[:, kw_idx]
        #     if filter_result.matcher_result.stem_result is not None:
        #         df[f"{prefix} - stem match"]      = stem_matches[:, kw_idx]

        #     if filter_result.matcher_result.similarity_result is not None:
        #         df[f"{prefix} - similarity match"] = similarity_matches[:, kw_idx]
        #         df[f"{prefix} - similarity"]      = cosine_sims[:, kw_idx]

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

        return df

    def to_csv(self, filter_result: MatchFilter.Result, metadata: Metadata, add_metadata: bool, add_results: bool) -> str:
        df = self.to_dataframe(filter_result, metadata.keywords, add_results)
        io = StringIO()
        df.to_csv(io, index=False)
        csv_string = io.getvalue()

        if add_metadata:
            csv_string = f"{metadata}\n{csv_string}"

        return csv_string

    def to_xlsx(self, filter_result: MatchFilter.Result, metadata: Metadata, add_metadata: bool, add_results: bool) -> bytes:
        df = self.to_dataframe(filter_result, metadata.keywords, add_results)
        io = BytesIO()
        with pd.ExcelWriter(io, engine="openpyxl") as writer:
            for source in df["source"].unique():
                source_df = df[df["source"] == source]
                source_df.to_excel(writer, sheet_name=source, index=False)
            if add_metadata:
                metadata_df = pd.DataFrame({
                    "timestamp": metadata.timestamp,
                    "keywords": [metadata.keywords],
                    "cos_threshold": metadata.cos_threshold
                })
                metadata_df.to_excel(writer, sheet_name="metadata", index=False)
        return io.getvalue()
    