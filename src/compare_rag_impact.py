"""Show how retrieval changes VibeMatcher recommendations versus baseline scoring."""

from __future__ import annotations

from pathlib import Path

from recommender import configure_logging, load_songs, run_recommendation_workflow


PROJECT_ROOT = Path(__file__).resolve().parent.parent


IMPACT_CASES = [
    {
        "name": "focus overrides pop defaults",
        "intent": "I need quiet focus music for coding homework in the rain.",
        "prefs": {"genre": "pop", "mood": "happy", "energy": 0.8},
        "expected_rag_genres": {"lofi", "ambient", "classical"},
    },
    {
        "name": "workout overrides chill defaults",
        "intent": "Give me high energy songs for a gym workout.",
        "prefs": {"genre": "lofi", "mood": "chill", "energy": 0.3},
        "expected_rag_genres": {"pop", "electronic", "rock"},
    },
    {
        "name": "calm reset overrides intense defaults",
        "intent": "I want soft calm music to relax before sleep.",
        "prefs": {"genre": "rock", "mood": "intense", "energy": 0.95},
        "expected_rag_genres": {"ambient", "folk", "classical", "lofi"},
    },
]


def main() -> None:
    configure_logging(str(PROJECT_ROOT / "logs" / "rag_impact.log"))
    songs = load_songs(str(PROJECT_ROOT / "data" / "songs.csv"))

    passed = 0
    changed = 0
    print("VibeMatcher RAG Impact Comparison")
    print()

    for case in IMPACT_CASES:
        baseline = run_recommendation_workflow(
            "",
            songs,
            user_prefs=case["prefs"],
            k=5,
            mode="balanced",
            lock_explicit_preferences=True,
        )
        rag = run_recommendation_workflow(
            case["intent"],
            songs,
            user_prefs=case["prefs"],
            k=5,
            mode="balanced",
            lock_explicit_preferences=False,
        )

        baseline_top = baseline["recommendations"][0][0]
        rag_top = rag["recommendations"][0][0]
        top_changed = baseline_top["id"] != rag_top["id"]
        target_match = rag_top["genre"] in case["expected_rag_genres"]
        changed += int(top_changed)
        passed += int(top_changed and target_match)

        print(case["name"])
        print(
            f"  baseline: {baseline_top['title']} ({baseline_top['genre']}), "
            f"confidence={baseline['confidence']:.2f}"
        )
        print(
            f"  with RAG:  {rag_top['title']} ({rag_top['genre']}), "
            f"confidence={rag['confidence']:.2f}"
        )
        print(f"  changed_top={top_changed} target_match={target_match}")
        print()

    print("Summary")
    print(f"Passed: {passed}/{len(IMPACT_CASES)}")
    print(f"Top recommendation changed: {changed}/{len(IMPACT_CASES)}")

    raise SystemExit(0 if passed == len(IMPACT_CASES) else 1)


if __name__ == "__main__":
    main()
