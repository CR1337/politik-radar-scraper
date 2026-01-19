import sys
import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from article_serializer import ArticleSerializer


MAX_INT: int = sys.maxsize * 2 + 1


def done():
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

    metadata = ArticleSerializer.Metadata(
        datetime.now(),
        keywords, 
        cos_threshold=st.session_state["cosine_threshold"]
    )

    metadata_df = pd.DataFrame({
        "timestamp": metadata.timestamp,
        "keywords": [keywords],
        "cos_threshold": metadata.cos_threshold
    })
    st.write("Metadaten")
    st.dataframe(
        metadata_df, 
        width="content", 
        height="stretch", 
        column_config={
            "timestamp": st.column_config.DateColumn("Abrufzeitpunkt"),
            "keywords": st.column_config.ListColumn("Schlagwörter"),
            "cos_threshold": st.column_config.ProgressColumn(
                "Ähnlichkeitsgrenzwert",
                format="%.4f",
                min_value=0,
                max_value=1
            )
        },
        hide_index=True
    )

    serializer = ArticleSerializer()
    
    df = serializer.to_dataframe(filter_result, keywords, True)
    st.write("Ergebnisse")
    st.dataframe(
        df,
        width="content",
        height="stretch",
        column_config={
            "timestamp": st.column_config.DateColumn("Datum"),
            "title": st.column_config.TextColumn("Titel"),
            "content": st.column_config.TextColumn("Text"),
            "link": st.column_config.LinkColumn("Link"),
            "source": st.column_config.TextColumn("Quelle")
        } | {
            f"{keyword} - exact match": st.column_config.CheckboxColumn(
                f"{keyword} - Exaktes Match"
            )
            for keyword in keywords
        } | {
            f"{keyword} - stem match": st.column_config.CheckboxColumn(
                f"{keyword} - Wortstamm Match"
            )
            for keyword in keywords
        } | {
            f"{keyword} - similarity match": st.column_config.CheckboxColumn(
                f"{keyword} - Ähnlichkeitsmatch"
            )
            for keyword in keywords
        } | {
            f"{keyword} - similarity": st.column_config.ProgressColumn(
                f"{keyword} - Ähnlichkeit",
                format="%.4f",
                min_value=0,
                max_value=1
            )
            for keyword in keywords
        },
        hide_index=True
    )

    options = ["Metadaten", "Match-Ergebnisse"]
    selection = st.segmented_control(
        "Zu Datei hinzufügen",
        options=options,
        default=[],
        selection_mode="multi"
    )
    add_metadata = options[0] in selection
    add_match_results = options[1] in selection

    st.download_button(
        "CSV-Datei herunterladen",
        data=serializer.to_csv(
            filter_result, 
            metadata,
            add_metadata,
            add_match_results
        ),
        file_name="data.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.download_button(
        "XLSX-Datei herunterladen",
        data=serializer.to_xlsx(
            filter_result, 
            metadata,
            add_metadata,
            add_match_results
        ),
        file_name="data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

    if st.button(
        label="Neue Datenabfrage",
        use_container_width=True
    ):
        st.session_state["state"] = "idle"
        st.rerun()