"""Compare baseline responses with specialized VibeMatcher responses."""

from __future__ import annotations

from pathlib import Path
from statistics import mean

from recommender import (
    compare_response_specialization,
    configure_logging,
    load_response_styles,
    load_songs,
    run_recommendation_workflow,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent


DEMO_CASES = [
    {
        "intent": "I need quiet focus music for coding homework in the rain.",
        "prefs": {"genre": "pop", "mood": "happy", "energy": 0.8},
    },
    {
        "intent": "Give me high energy songs for a gym workout.",
        "prefs": {"genre": "lofi", "mood": "chill", "energy": 0.3},
    },
    {
        "intent": "I want soft calm music to relax before sleep.",
        "prefs": {"genre": "rock", "mood": "intense", "energy": 0.9},
    },
]


def main() -> None:
    configure_logging(str(PROJECT_ROOT / "logs" / "specialization.log"))
    songs = load_songs(str(PROJECT_ROOT / "data" / "songs.csv"))
    style = load_response_styles(str(PROJECT_ROOT / "data" / "response_styles.csv"))[0]

    comparisons = []
    print("VibeMatcher Specialization Comparison")
    print(f"Style: {style.label}")
    print(f"Tone rules: {style.tone_rules}")
    print()

    for index, case in enumerate(DEMO_CASES, start=1):
        result = run_recommendation_workflow(
            case["intent"],
            songs,
            user_prefs=case["prefs"],
            k=5,
            mode="balanced",
            lock_explicit_preferences=False,
        )
        comparison = compare_response_specialization(result, style=style)
        comparisons.append(comparison)

        print(f"Case {index}: {case['intent']}")
        print("Baseline:")
        print(comparison["baseline"])
        print("Specialized:")
        print(comparison["specialized"])
        print(
            "Metrics: "
            f"evidence_marker_delta={comparison['evidence_marker_delta']}, "
            f"word_count_delta={comparison['word_count_delta']}"
        )
        print()

    avg_evidence_delta = mean(item["evidence_marker_delta"] for item in comparisons)
    avg_word_delta = mean(item["word_count_delta"] for item in comparisons)
    passed = all(
        item["evidence_marker_delta"] >= 3 and item["word_count_delta"] > 20
        for item in comparisons
    )

    print("Summary")
    print(f"Passed: {sum(1 for item in comparisons if item['evidence_marker_delta'] >= 3)}/{len(comparisons)}")
    print(f"Average evidence marker delta: {avg_evidence_delta:.1f}")
    print(f"Average word count delta: {avg_word_delta:.1f}")

    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
