import sys
import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from article_accumulator import ArticleAccumulator
from dataframe_serializer import DataframeSerializer


MAX_INT: int = sys.maxsize * 2 + 1


def done():
    col1, col2 = st.columns([1, 40])
    with col1:
        st.image("img/funk.png")

    with col2:
        st.title("politik.radar Scraper")
    st_autorefresh(interval=MAX_INT, limit=1, key="refresh_off")

    progress = st.session_state["progress"]
    print(progress.error_messages)
    thread = st.session_state["thread"]
    filter_result = thread.result()
    keywords = st.session_state["keywords"]

    if len(progress.error_messages):
        st.write("Fehlermeldungen")
        for msg in progress.error_messages:
            st.write(msg)

    metadata = DataframeSerializer.Metadata(
        datetime.now(), keywords, cos_threshold=st.session_state["cosine_threshold"]
    )

    metadata_df = pd.DataFrame(
        {
            "timestamp": metadata.timestamp,
            "keywords": [keywords],
            "cos_threshold": metadata.cos_threshold,
        }
    )
    st.write("Metadaten")
    st.dataframe(
        metadata_df,
        width="content",
        height="stretch",
        column_config={
            "timestamp": st.column_config.DateColumn("Abrufzeitpunkt"),
            "keywords": st.column_config.ListColumn("Schlagwörter"),
            "cos_threshold": st.column_config.ProgressColumn(
                "Ähnlichkeitsgrenzwert", format="%.4f", min_value=0, max_value=1
            ),
        },
        hide_index=True,
    )

    article_accumulator = ArticleAccumulator()

    df, bool_columns, df_keywords = article_accumulator.to_dataframe(
        filter_result, keywords
    )
    df["select"] = df[bool_columns].any(axis=1).astype(bool)
    base_columns = [
        "select",
        "timestamp",
        "medium_organisation",
        "title",
        "content",
        "link",
        "source",
    ]
    df["Stichwörter"] = df_keywords

    other_columns = [col for col in df.columns if col not in base_columns]

    df = df[base_columns + other_columns]

    st.write("Ergebnisse")
    edited_df = st.data_editor(
        df,
        width="content",
        height="stretch",
        column_config={
            "select": st.column_config.CheckboxColumn("Auswählen"),
            "timestamp": st.column_config.TextColumn("Datum", disabled=True),
            "medium_organisation": st.column_config.TextColumn(
                "Medium/Organisation", disabled=True
            ),
            "title": st.column_config.TextColumn("Titel", disabled=True),
            "content": st.column_config.TextColumn("Text", disabled=True),
            "link": st.column_config.LinkColumn("Link", disabled=True),
            "source": st.column_config.TextColumn("Quelle", disabled=True),
        }
        | {
            f"{keyword} - exact match": st.column_config.CheckboxColumn(
                f"{keyword} - Exaktes Match", disabled=True
            )
            for keyword in keywords
        }
        | {
            f"{keyword} - stem match": st.column_config.CheckboxColumn(
                f"{keyword} - Wortstamm Match", disabled=True
            )
            for keyword in keywords
        }
        | {
            f"{keyword} - similarity match": st.column_config.CheckboxColumn(
                f"{keyword} - Ähnlichkeitsmatch", disabled=True
            )
            for keyword in keywords
        }
        | {
            f"{keyword} - similarity": st.column_config.ProgressColumn(
                f"{keyword} - Ähnlichkeit", format="%.4f", min_value=0, max_value=1
            )
            for keyword in keywords
        },
        hide_index=True,
    )

    selected_df = edited_df[edited_df["select"]].drop("select", axis=1)

    options = ["Metadaten", "Match-Ergebnisse", "Stichwort-Spalte"]
    selection = st.segmented_control(
        "Zu Datei hinzufügen", options=options, default=[], selection_mode="multi"
    )
    add_metadata = options[0] in selection
    add_match_results = options[1] in selection
    add_keywords = options[2] in selection

    serializer = DataframeSerializer()

    if len(selected_df) > 0:
        st.download_button(
            "CSV-Datei herunterladen",
            data=serializer.to_csv(
                selected_df, metadata, add_metadata, add_match_results, add_keywords
            ),
            file_name="data.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.download_button(
            "XLSX-Datei herunterladen",
            data=serializer.to_xlsx(
                selected_df, metadata, add_metadata, add_match_results, add_keywords
            ),
            file_name="data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    else:
        st.button("CSV-Datei herunterladen", disabled=True, use_container_width=True)
        st.button("XLSX-Datei herunterladen", disabled=True, use_container_width=True)

    if st.button(label="Neue Datenabfrage", use_container_width=True):
        st.session_state["state"] = "idle"
        st.rerun()
