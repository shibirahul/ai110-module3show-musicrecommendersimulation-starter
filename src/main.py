"""Command line demo for the VibeMatcher applied AI system."""

from __future__ import annotations

from pathlib import Path

from tabulate import tabulate

from recommender import (
    configure_logging,
    load_songs,
    run_recommendation_workflow,
)


SAMPLE_CASES = [
    {
        "name": "Deep Focus Coding",
        "intent": "I need quiet focus music for coding homework in the rain.",
        "prefs": {
            "genre": "pop",
            "mood": "happy",
            "energy": 0.7,
            "likes_acoustic": False,
            "prefers_popular": False,
            "decade": "2020s",
            "detailed_mood": "upbeat",
        },
    },
    {
        "name": "Workout Push",
        "intent": "Give me high energy songs for a gym workout.",
        "prefs": {
            "genre": "rock",
            "mood": "intense",
            "energy": 0.8,
            "likes_acoustic": False,
            "prefers_popular": True,
            "decade": "2010s",
            "detailed_mood": "motivational",
        },
    },
    {
        "name": "Calm Reset",
        "intent": "I want soft calm music to relax before sleep.",
        "prefs": {
            "genre": "folk",
            "mood": "calm",
            "energy": 0.4,
            "likes_acoustic": True,
            "prefers_popular": False,
            "decade": "2020s",
            "detailed_mood": "peaceful",
        },
    },
]


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    configure_logging(str(project_root / "logs" / "recommender.log"))
    songs = load_songs(str(project_root / "data" / "songs.csv"))

    for case in SAMPLE_CASES:
        result = run_recommendation_workflow(
            case["intent"],
            songs,
            user_prefs=case["prefs"],
            k=5,
            mode="balanced",
            lock_explicit_preferences=False,
        )
        print(f"\n=== {case['name']} ===")
        print(f"Intent: {case['intent']}")
        print(f"Confidence: {result['confidence']:.2f}")

        if result["warnings"]:
            print("Warnings:")
            for warning in result["warnings"]:
                print(f"- {warning}")

        print("\nWorkflow:")
        for step in result["plan_steps"]:
            print(f"- {step}")

        table_data = []
        for song, score, explanation in result["recommendations"]:
            table_data.append(
                [
                    song["title"],
                    song["artist"],
                    song["genre"],
                    f"{score:.2f}",
                    explanation,
                ]
            )
        print(
            tabulate(
                table_data,
                headers=["Title", "Artist", "Genre", "Score", "Reasons"],
                tablefmt="grid",
            )
        )


if __name__ == "__main__":
    main()
