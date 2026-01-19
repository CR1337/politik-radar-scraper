import streamlit as st
import json
from typing import List
from datetime import datetime, time, timedelta
from thread import ThreadWithResult
from scrapers.scrapers import ALL_SCRAPERS
from scrapers.scraper import Scraper
from matching.matcher import Matcher, SubMatcherType, ExactSubMatcher, StemSubMatcher, SimilaritySubMatcher 
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
from matching.match_filter import MatchFilter
import traceback


KEYWORDS_FILENAME: str = "keywords.json"
WEEK: int = 7  # days


@st.cache_data
def get_keywords() -> List[str]:
    with open(KEYWORDS_FILENAME, 'r') as file:
        keyword_data = json.load(file)
    all_keywords = []
    for keywords in keyword_data["topics"].values():
        all_keywords.extend(keywords)
    return all_keywords


def _worker(
    scraper_parameters: Scraper.Parameters, 
    matcher_parameters: Matcher.Parameters, 
    keywords: List[str]
) -> MatchFilter.Result:
    progress = st.session_state["progress"]

    selected_scrapers = st.session_state["selected_scrapers"]
    articles = []

    for scraper in progress.start_iteration(
        selected_scrapers, 
        total=len(selected_scrapers), 
        desc="Running Scrapers"
    ):
        try:
            articles.extend(scraper.scrape(scraper_parameters, progress))
        except Exception as e:
            print("### Exception while Scraping", flush=True)
            print(e, flush=True)
            print(traceback.format_exc(), flush=True)
            progress.add_eadd_error_message(f"Fehler beim Scrapen von: {scraper.SOURCE}")

    contents = [a.content for a in articles]
    try:
        matcher_result = Matcher().match(
            matcher_parameters, 
            keywords, 
            contents,
            progress
        )
    except Exception as e:
        print("### Exception while Matching", flush=True)
        print(e, flush=True)
        print(traceback.format_exc(), flush=True)
        return MatchFilter.Result.empty()

    # keywords = st.session_state["keywords"]
    # try:
    #     filter_result = MatchFilter().filter_articles(articles, matcher_result, keywords, progress)
    # except Exception as e:
    #     print("### Excpetion while Filtering", flush=True)
    #     print(e, flush=True)
    #     print(traceback.format_exc(), flush=True)
    #     return MatchFilter.Result.empty()

    st.session_state["state"] = "done"

    filter_result = MatchFilter.Result(articles, matcher_result)

    return filter_result


def _start_workload(
    keywords: List[str],
    match_options: List[str], 
    match_selection: List[str],
    selected_scrapers: List[Scraper],
    start_date: datetime,
    end_date: datetime,
    cosine_threshold: float
):
    st.session_state["state"] = "running"

    match_exact = match_options[0] in match_selection
    match_stem = match_options[1] in match_selection
    match_similarity = match_options[2] in match_selection

    sub_matcher_selection = set()
    if match_exact:
        sub_matcher_selection.add(SubMatcherType.EXACT)
    if match_stem:
        sub_matcher_selection.add(SubMatcherType.STEM)
    if match_similarity:
        sub_matcher_selection.add(SubMatcherType.SIMILARITY)

    scraper_parameters = Scraper.Parameters(start_date, end_date)
    matcher_parameters = Matcher.Parameters(
        sub_matcher_selection,
        ExactSubMatcher.Parameters() if match_exact else None,
        StemSubMatcher.Parameters() if match_stem else None,
        SimilaritySubMatcher.Parameters(cosine_threshold) if match_similarity else None
    )

    st.session_state["keywords"] = keywords
    st.session_state["matcher_parameters"] = matcher_parameters
    st.session_state["selected_scrapers"] = selected_scrapers

    thread = ThreadWithResult(target=_worker, args=(scraper_parameters, matcher_parameters, keywords))
    add_script_run_ctx(thread, get_script_run_ctx())
    st.session_state["thread"] = thread
    thread.start()
    st.rerun()


def idle():
    keyword_options = get_keywords()
    keywords = st.multiselect(
        label="Schlagwörter",
        options=keyword_options,
        default=keyword_options,
        accept_new_options=True
    )

    source_options = list(ALL_SCRAPERS.keys())
    source_selection = st.segmented_control(
        label="Quellen",
        options=source_options,
        default=source_options,
        selection_mode="multi"
    )
    selected_scrapers = [ALL_SCRAPERS[s] for s in source_selection]
    
    match_options = ["Exakt", "Wortstamm", "Ähnlichkeit"]
    default_options = match_options[:-1]
    match_selection = st.segmented_control(
        label="Match-Methoden",
        options=match_options,
        default=default_options,
        selection_mode="multi"
    )

    if "Ähnlichkeit" in match_selection:
        cosine_threshold = st.slider(
            label="Minimale Ähnlichkeit",
            min_value=0.0,
            max_value=1.0,
            value=0.2,
            step=0.01
        )
        st.session_state["cosine_threshold"] = cosine_threshold
    else:
        cosine_threshold = 0.0
        st.session_state["cosine_threshold"] = None

    columns = st.columns(2)

    start_date = datetime.combine(columns[0].date_input(
        label="Startdatum",
        value=datetime.now() - timedelta(days=WEEK),
        max_value="today"
    ), time.min)

    end_date = datetime.combine(columns[1].date_input(
        label="Enddatum",
        value="today",
        max_value="today"
    ), time.min)

    if st.button("Starten", use_container_width=True):
        _start_workload(
            keywords,
            match_options,
            match_selection,
            selected_scrapers,
            start_date,
            end_date,
            cosine_threshold
        )


        
        