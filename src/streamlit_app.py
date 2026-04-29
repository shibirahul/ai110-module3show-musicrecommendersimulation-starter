"""Streamlit interface for the VibeMatcher applied AI system."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from recommender import (
    configure_logging,
    load_intent_contexts,
    load_songs,
    run_recommendation_workflow,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
st.set_page_config(page_title="VibeMatcher Applied AI", page_icon="🎵", layout="wide")


@st.cache_data
def get_songs() -> list[dict]:
    return load_songs(str(PROJECT_ROOT / "data" / "songs.csv"))


@st.cache_data
def get_contexts() -> list:
    return load_intent_contexts(str(PROJECT_ROOT / "data" / "intent_guides.csv"))


def build_user_prefs(songs: list[dict]) -> dict:
    genres = sorted({song["genre"] for song in songs})
    moods = sorted({song["mood"] for song in songs})
    decades = sorted({song["decade"] for song in songs})
    detailed_moods = sorted({song["detailed_mood"] for song in songs})

    st.sidebar.header("Preference Controls")
    genre = st.sidebar.selectbox("Preferred genre", genres, index=_index_or_zero(genres, "pop"))
    mood = st.sidebar.selectbox("Preferred mood", moods, index=_index_or_zero(moods, "happy"))
    energy = st.sidebar.slider("Preferred energy", 0.0, 1.0, 0.7, 0.01)
    likes_acoustic = st.sidebar.checkbox("Likes acoustic songs", value=False)
    prefers_popular = st.sidebar.checkbox("Prefers popular songs", value=True)
    decade = st.sidebar.selectbox("Favorite decade", decades, index=_index_or_zero(decades, "2020s"))
    detailed_mood = st.sidebar.selectbox(
        "Preferred detailed mood",
        detailed_moods,
        index=_index_or_zero(detailed_moods, "upbeat"),
    )

    return {
        "genre": genre,
        "mood": mood,
        "energy": energy,
        "likes_acoustic": likes_acoustic,
        "prefers_popular": prefers_popular,
        "decade": decade,
        "detailed_mood": detailed_mood,
    }


def render_recommendations(result: dict) -> None:
    confidence = result["confidence"]
    st.metric("System confidence", f"{confidence:.2f}")

    if result["warnings"]:
        for warning in result["warnings"]:
            st.warning(warning)

    st.subheader("Specialized AI Response")
    st.write(result["specialized_response"])

    with st.expander("Compare baseline vs specialized response"):
        metrics = result["specialization_metrics"]
        st.write("Baseline response:")
        st.code(metrics["baseline"], language="text")
        st.write("Specialized response:")
        st.code(metrics["specialized"], language="text")
        st.write(
            {
                "evidence_marker_delta": metrics["evidence_marker_delta"],
                "word_count_delta": metrics["word_count_delta"],
            }
        )

    rows = []
    for song, score, explanation in result["recommendations"]:
        rows.append(
            {
                "Title": song["title"],
                "Artist": song["artist"],
                "Genre": song["genre"],
                "Mood": song["mood"],
                "Energy": song["energy"],
                "Score": round(score, 2),
                "Reasons": explanation,
            }
        )

    st.subheader("Recommended Songs")
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)

    st.subheader("AI Workflow Trace")
    for step in result["plan_steps"]:
        st.write(f"- {step}")

    st.subheader("Retrieved Listening Guides")
    context_rows = []
    for context in result["retrieved_contexts"]:
        context_rows.append(
            {
                "Guide": context.name,
                "Score": context.score,
                "Matched Terms": ", ".join(context.matched_terms),
                "Rationale": context.rationale,
                "Guardrail": context.guardrail,
            }
        )
    if context_rows:
        st.dataframe(pd.DataFrame(context_rows), hide_index=True, use_container_width=True)
    else:
        st.info("No listening guide was retrieved for this input.")


def _index_or_zero(values: list[str], target: str) -> int:
    return values.index(target) if target in values else 0


configure_logging(str(PROJECT_ROOT / "logs" / "recommender.log"))

st.title("VibeMatcher Applied AI System")
st.write(
    "Enter a listening goal, then the system retrieves intent guidance, plans guarded preferences, "
    "scores the catalog, and reports confidence."
)

songs = get_songs()
contexts = get_contexts()

intent_text = st.text_area(
    "Listening goal",
    value="I need quiet focus music for coding homework in the rain.",
    height=90,
)

col_a, col_b, col_c = st.columns([1, 1, 1])
with col_a:
    mode = st.selectbox("Ranking mode", ["balanced", "genre_first", "energy_focus"])
with col_b:
    top_k = st.slider("Number of recommendations", 3, 10, 5)
with col_c:
    lock_explicit = st.checkbox("Lock sidebar preferences", value=False)

user_prefs = build_user_prefs(songs)
result = run_recommendation_workflow(
    intent_text,
    songs,
    user_prefs=user_prefs,
    contexts=contexts,
    k=top_k,
    mode=mode,
    lock_explicit_preferences=lock_explicit,
)
render_recommendations(result)
