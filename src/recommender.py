from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Load songs from a CSV file and convert numerical fields to appropriate types.
    
    Args:
        csv_path: Path to the CSV file containing song data.
    
    Returns:
        List of dictionaries, each representing a song.
    """
    import csv
    songs = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numerical fields
            row['id'] = int(row['id'])
            row['energy'] = float(row['energy'])
            row['tempo_bpm'] = float(row['tempo_bpm'])
            row['valence'] = float(row['valence'])
            row['danceability'] = float(row['danceability'])
            row['acousticness'] = float(row['acousticness'])
            songs.append(row)
    print(f"Loading songs from {csv_path}...")
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Score a single song based on user preferences.
    
    Awards points for genre match (+2.0), mood match (+1.0), and energy similarity (0-1).
    
    Args:
        user_prefs: Dictionary with user preferences (genre, mood, energy).
        song: Dictionary representing a song.
    
    Returns:
        Tuple of (total_score, list_of_reasons).
    """
    score = 0.0
    reasons = []
    
    # Genre match
    if song['genre'] == user_prefs.get('genre'):
        score += 2.0
        reasons.append("genre match (+2.0)")
    
    # Mood match
    if song['mood'] == user_prefs.get('mood'):
        score += 1.0
        reasons.append("mood match (+1.0)")
    
    # Energy similarity
    energy_diff = abs(song['energy'] - user_prefs.get('energy', 0.5))
    energy_sim = 1.0 - energy_diff
    score += energy_sim
    reasons.append(f"energy similarity ({energy_sim:.2f})")
    
    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Recommend top k songs based on user preferences.
    
    Scores all songs, sorts by score descending, returns top k with explanations.
    
    Args:
        user_prefs: User preferences dictionary.
        songs: List of song dictionaries.
        k: Number of recommendations to return.
    
    Returns:
        List of tuples (song_dict, score, explanation_string).
    """
    scored_songs = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = ", ".join(reasons)
        scored_songs.append((song, score, explanation))
    
    # Sort by score descending
    scored_songs.sort(key=lambda x: x[1], reverse=True)
    
    # Return top k
    return scored_songs[:k]
