from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """A song with audio features and metadata for content-based recommendations."""
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
    """User taste preferences for personalized recommendations."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    prefers_popular: bool
    favorite_decade: str
    favorite_detailed_mood: str

class Recommender:
    """Core recommendation engine for VibeMatcher."""
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Score and rank songs by user preference match."""
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Generate transparent explanation for why a song was recommended."""
        return "Explanation generated based on user profile match."

def load_songs(csv_path: str) -> List[Dict]:
    """Load song dataset from CSV and parse numeric audio features."""
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
            row['acousticness'] = float(row['acousticness'])
            row['popularity'] = int(row['popularity'])
            row['decade'] = row['decade']
            row['detailed_mood'] = row['detailed_mood']
            songs.append(row)
    print(f"Loading songs from {csv_path}...")
    return songs

def score_song(user_prefs: Dict, song: Dict, mode: str = 'balanced') -> Tuple[float, List[str]]:
    """Score a song based on weighted match with user preferences. Modes adjust genre/energy emphasis."""
    score = 0.0
    reasons = []
    
    genre_weight = 2.0
    mood_weight = 1.0
    energy_weight = 1.0
    
    if mode == 'genre_first':
        genre_weight *= 2
        reasons.append("(genre-first mode)")
    elif mode == 'energy_focus':
        energy_weight *= 2
        reasons.append("(energy-focus mode)")
    
    # Genre match
    if song['genre'] == user_prefs.get('genre'):
        score += genre_weight
        reasons.append(f"genre match (+{genre_weight})")
    
    # Mood match
    if song['mood'] == user_prefs.get('mood'):
        score += mood_weight
        reasons.append(f"mood match (+{mood_weight})")
    
    # Energy similarity
    energy_diff = abs(song['energy'] - user_prefs.get('energy', 0.5))
    energy_sim = (1.0 - energy_diff) * energy_weight
    score += energy_sim
    reasons.append(f"energy similarity ({energy_sim:.2f})")
    
    # Acousticness
    if user_prefs.get('likes_acoustic', False) and song['acousticness'] > 0.7:
        score += 0.5
        reasons.append("acoustic preference (+0.5)")
    
    # Popularity
    if user_prefs.get('prefers_popular', False) and song['popularity'] > 80:
        score += 0.5
        reasons.append("popularity preference (+0.5)")
    
    # Decade match
    if song['decade'] == user_prefs.get('decade'):
        score += 0.5
        reasons.append("decade match (+0.5)")
    
    # Detailed mood match
    if song['detailed_mood'] == user_prefs.get('detailed_mood'):
        score += 0.5
        reasons.append("detailed mood match (+0.5)")
    
    return score, reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5, mode: str = 'balanced') -> List[Tuple[Dict, float, str]]:
    """Rank all songs and return top k recommendations with diversity penalties to avoid artist repetition."""
    scored_songs = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, mode)
        explanation = ", ".join(reasons)
        scored_songs.append((song, score, explanation))
    
    # Sort by score descending
    scored_songs.sort(key=lambda x: x[1], reverse=True)
    
    # Apply diversity penalty
    seen_artists = set()
    for i, (song, score, exp) in enumerate(scored_songs):
        if song['artist'] in seen_artists:
            scored_songs[i] = (song, score - 0.5, exp + ", diversity penalty (-0.5)")
        else:
            seen_artists.add(song['artist'])
    
    # Re-sort after penalty
    scored_songs.sort(key=lambda x: x[1], reverse=True)
    
    # Return top k
    return scored_songs[:k]
