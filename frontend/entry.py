import streamlit as st
from frontend.idle import idle
from frontend.running import running
from frontend.done import done
from progress import Progress


def entry():
    st.set_page_config(layout="wide")

    if "state" not in st.session_state:
        st.session_state["state"] = "idle"
    
    if "progress" not in st.session_state:
        st.session_state["progress"] = Progress()

    match st.session_state["state"]:
        case "idle":
            idle()
        case "running":
            running()
        case "done":
            done()
            