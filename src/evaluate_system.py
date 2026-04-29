"""Reliability harness for the VibeMatcher applied AI system."""

from __future__ import annotations

from pathlib import Path
from statistics import mean

from recommender import configure_logging, load_songs, run_recommendation_workflow


PROJECT_ROOT = Path(__file__).resolve().parent.parent


EVALUATION_CASES = [
    {
        "name": "focus query retrieves calm study music",
        "intent": "I need quiet focus music for coding homework.",
        "prefs": {"genre": "pop", "mood": "happy", "energy": 0.8},
        "expected_genres": {"lofi", "ambient", "classical"},
        "min_confidence": 0.55,
    },
    {
        "name": "workout query favors energetic songs",
        "intent": "Give me high energy songs for a gym workout.",
        "prefs": {"genre": "lofi", "mood": "chill", "energy": 0.2},
        "expected_genres": {"pop", "electronic", "rock"},
        "min_energy": 0.8,
        "min_confidence": 0.55,
    },
    {
        "name": "calm query favors acoustic low-energy songs",
        "intent": "I want soft calm music to relax before sleep.",
        "prefs": {"genre": "rock", "mood": "intense", "energy": 0.95},
        "expected_acoustic": True,
        "max_energy": 0.5,
        "min_confidence": 0.55,
    },
    {
        "name": "invalid energy is guarded",
        "intent": "party music with friends",
        "prefs": {"genre": "electronic", "mood": "happy", "energy": 8},
        "expects_warning": "Energy was clamped",
        "min_confidence": 0.5,
    },
    {
        "name": "unknown query still returns safe fallback",
        "intent": "make something for an unlisted alien opera use case",
        "prefs": {"genre": "jazz", "mood": "relaxed", "energy": 0.5},
        "expects_warning": "No matching listening guide",
        "min_confidence": 0.45,
    },
]


def evaluate_case(case: dict, songs: list[dict]) -> dict:
    result = run_recommendation_workflow(
        case["intent"],
        songs,
        user_prefs=case["prefs"],
        k=5,
        mode="balanced",
        lock_explicit_preferences=False,
    )
    top_song = result["recommendations"][0][0]
    checks = []

    if "expected_genres" in case:
        checks.append(top_song["genre"] in case["expected_genres"])
    if "min_energy" in case:
        checks.append(top_song["energy"] >= case["min_energy"])
    if "max_energy" in case:
        checks.append(top_song["energy"] <= case["max_energy"])
    if case.get("expected_acoustic"):
        checks.append(top_song["acousticness"] > 0.7)
    if "expects_warning" in case:
        checks.append(any(case["expects_warning"] in warning for warning in result["warnings"]))

    checks.append(result["confidence"] >= case["min_confidence"])
    passed = all(checks)

    return {
        "name": case["name"],
        "passed": passed,
        "confidence": result["confidence"],
        "top_song": top_song["title"],
        "top_artist": top_song["artist"],
        "top_genre": top_song["genre"],
        "warnings": result["warnings"],
    }


def main() -> None:
    configure_logging(str(PROJECT_ROOT / "logs" / "evaluation.log"))
    songs = load_songs(str(PROJECT_ROOT / "data" / "songs.csv"))
    results = [evaluate_case(case, songs) for case in EVALUATION_CASES]

    passed = sum(1 for result in results if result["passed"])
    average_confidence = mean(result["confidence"] for result in results)

    print("VibeMatcher Reliability Evaluation")
    print(f"Passed: {passed}/{len(results)}")
    print(f"Average confidence: {average_confidence:.2f}")
    print()

    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        print(
            f"{status} | {result['name']} | confidence={result['confidence']:.2f} | "
            f"top={result['top_song']} by {result['top_artist']} ({result['top_genre']})"
        )
        if result["warnings"]:
            print("  warnings: " + "; ".join(result["warnings"]))

    raise SystemExit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
