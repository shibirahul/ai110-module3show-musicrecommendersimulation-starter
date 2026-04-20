import os
from pathlib import Path

import pandas as pd
import streamlit as st

from recommender import load_songs, recommend_songs


@st.cache_data
def get_songs() -> list[dict]:
    script_dir = Path(__file__).resolve().parent
    data_path = script_dir.parent / "data" / "songs.csv"
    return load_songs(str(data_path))


def build_user_prefs() -> dict:
    genres = sorted({song['genre'] for song in songs})
    moods = sorted({song['mood'] for song in songs})
    decades = sorted({song['decade'] for song in songs})
    detailed_moods = sorted({song['detailed_mood'] for song in songs})

    st.sidebar.header("User Preferences")
    genre = st.sidebar.selectbox("Preferred genre", genres, index=genres.index("pop") if "pop" in genres else 0)
    mood = st.sidebar.selectbox("Preferred mood", moods, index=moods.index("happy") if "happy" in moods else 0)
    energy = st.sidebar.slider("Preferred energy", 0.0, 1.0, 0.7, 0.01)
    likes_acoustic = st.sidebar.checkbox("Likes acoustic songs", value=False)
    prefers_popular = st.sidebar.checkbox("Prefers popular songs", value=True)
    decade = st.sidebar.selectbox("Favorite decade", decades, index=decades.index("2010s") if "2010s" in decades else 0)
    detailed_mood = st.sidebar.selectbox("Preferred detailed mood", detailed_moods, index=detailed_moods.index("upbeat") if "upbeat" in detailed_moods else 0)
    mode = st.sidebar.selectbox("Ranking mode", ["balanced", "genre_first", "energy_focus"])
    top_k = st.sidebar.slider("Number of recommendations", 3, 10, 5)

    return {
        "genre": genre,
        "mood": mood,
        "energy": energy,
        "likes_acoustic": likes_acoustic,
        "prefers_popular": prefers_popular,
        "decade": decade,
        "detailed_mood": detailed_mood,
        "mode": mode,
        "top_k": top_k,
    }


def render_recommendations(user_prefs: dict, songs: list[dict]) -> None:
    st.subheader("Recommended Songs")
    recommendations = recommend_songs(user_prefs, songs, k=user_prefs["top_k"], mode=user_prefs["mode"])

    rows = []
    for song, score, explanation in recommendations:
        rows.append({
            "Title": song["title"],
            "Artist": song["artist"],
            "Genre": song["genre"],
            "Energy": song["energy"],
            "Score": round(score, 2),
            "Reasons": explanation,
        })

    df = pd.DataFrame(rows)
    st.table(df)

    with st.expander("Show raw recommendations data"):
        st.write(recommendations)


st.title("VibeMatcher 1.0 — Streamlit Music Recommender")
st.write(
    "Choose your preferences in the sidebar and the recommender will show the top songs from the dataset. "
    "Scores are based on genre, mood, energy, popularity, acoustic preference, decade, and detailed mood."
)

songs = get_songs()
user_prefs = build_user_prefs()
render_recommendations(user_prefs, songs)
