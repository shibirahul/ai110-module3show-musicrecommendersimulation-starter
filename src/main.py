"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import os
from recommender import load_songs, recommend_songs
from tabulate import tabulate


def main() -> None:
    # Get the directory of this script, then go up to parent and to data
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')
    csv_path = os.path.join(data_dir, 'songs.csv')
    songs = load_songs(csv_path) 

    # Define multiple profiles with extended prefs
    profiles = [
        {
            "name": "High-Energy Pop Fan",
            "prefs": {
                "genre": "pop", 
                "mood": "happy", 
                "energy": 0.8,
                "likes_acoustic": False,
                "prefers_popular": True,
                "decade": "2010s",
                "detailed_mood": "upbeat"
            }
        },
        {
            "name": "Chill Lofi Listener",
            "prefs": {
                "genre": "lofi", 
                "mood": "chill", 
                "energy": 0.4,
                "likes_acoustic": True,
                "prefers_popular": False,
                "decade": "2020s",
                "detailed_mood": "relaxed"
            }
        },
        {
            "name": "Intense Rock Lover",
            "prefs": {
                "genre": "rock", 
                "mood": "intense", 
                "energy": 0.9,
                "likes_acoustic": False,
                "prefers_popular": False,
                "decade": "1990s",
                "detailed_mood": "aggressive"
            }
        },
    ]

    modes = ['balanced', 'genre_first', 'energy_focus']

    for profile in profiles:
        for mode in modes:
            print(f"\n=== {profile['name']} ({mode} mode) ===")
            recommendations = recommend_songs(profile['prefs'], songs, k=5, mode=mode)
            
            # Prepare table data
            table_data = []
            for rec in recommendations:
                song, score, explanation = rec
                table_data.append([
                    song['title'],
                    song['artist'],
                    f"{score:.2f}",
                    explanation
                ])
            
            # Print table
            headers = ["Title", "Artist", "Score", "Reasons"]
            print(tabulate(table_data, headers=headers, tablefmt="grid"))


if __name__ == "__main__":
    main()
