from pathlib import Path

from src.recommender import (
    Recommender,
    Song,
    UserProfile,
    compare_response_specialization,
    load_intent_contexts,
    load_response_styles,
    load_songs,
    plan_preferences,
    retrieve_intent_contexts,
    run_recommendation_workflow,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Second Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert "genre match" in explanation


def test_retrieval_finds_focus_context():
    contexts = load_intent_contexts(str(PROJECT_ROOT / "data" / "intent_guides.csv"))
    retrieved = retrieve_intent_contexts("coding focus homework", contexts)

    assert retrieved
    assert retrieved[0].id == "focus_coding"
    assert "coding" in retrieved[0].matched_terms


def test_workflow_uses_retrieved_context_over_default_preferences():
    songs = load_songs(str(PROJECT_ROOT / "data" / "songs.csv"))
    result = run_recommendation_workflow(
        "quiet focus music for coding",
        songs,
        user_prefs={"genre": "pop", "mood": "happy", "energy": 0.9},
        k=3,
        mode="balanced",
        lock_explicit_preferences=False,
    )

    assert result["preferences"]["genre"] == "lofi"
    assert result["recommendations"][0][0]["genre"] == "lofi"
    assert result["confidence"] >= 0.55


def test_plan_preferences_clamps_invalid_energy():
    songs = load_songs(str(PROJECT_ROOT / "data" / "songs.csv"))
    planned, _steps, warnings = plan_preferences(
        {"genre": "pop", "mood": "happy", "energy": 8},
        songs,
        retrieved_contexts=[],
    )

    assert planned["energy"] == 1.0
    assert any("clamped" in warning for warning in warnings)


def test_specialized_response_differs_from_baseline():
    songs = load_songs(str(PROJECT_ROOT / "data" / "songs.csv"))
    style = load_response_styles(str(PROJECT_ROOT / "data" / "response_styles.csv"))[0]
    result = run_recommendation_workflow(
        "Give me high energy songs for a gym workout.",
        songs,
        user_prefs={"genre": "lofi", "mood": "chill", "energy": 0.3},
    )

    comparison = compare_response_specialization(result, style=style)

    assert "Confidence:" in comparison["specialized"]
    assert "Evidence:" in comparison["specialized"]
    assert comparison["evidence_marker_delta"] >= 3
    assert comparison["word_count_delta"] > 20
