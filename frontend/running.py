import streamlit as st
from streamlit_autorefresh import st_autorefresh


REFRESH_INTERVAL: int = 500  # ms


def running():
    progress = st.session_state["progress"]
    st_autorefresh(interval=REFRESH_INTERVAL, limit=None, key="refresh")
    
    for progress_, total, desc in zip(
        progress.progresses,
        progress.totals,
        progress.descs
    ):
        value = progress_ / total
        st.progress(value, desc)
    