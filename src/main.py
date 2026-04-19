"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("../data/songs.csv") 

    # Define multiple profiles
    profiles = [
        {"name": "High-Energy Pop", "prefs": {"genre": "pop", "mood": "happy", "energy": 0.8}},
        {"name": "Chill Lofi", "prefs": {"genre": "lofi", "mood": "chill", "energy": 0.4}},
        {"name": "Intense Rock", "prefs": {"genre": "rock", "mood": "intense", "energy": 0.9}},
    ]

    for profile in profiles:
        print(f"\n=== {profile['name']} ===")
        recommendations = recommend_songs(profile['prefs'], songs, k=5)
        for rec in recommendations:
            song, score, explanation = rec
            print(f"{song['title']} by {song['artist']}")
            print(f"Score: {score:.2f}")
            print(f"Reasons: {explanation}")
            print("-" * 40)


if __name__ == "__main__":
    main()
