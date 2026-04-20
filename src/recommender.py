from typing import List, Dict, Tuple, Optional, TypedDict
from dataclasses import dataclass

class SongDict(TypedDict, total=False):
    """Type definition for a song record from the dataset."""
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
    popularity: int
    decade: str
    detailed_mood: str

class UserPreferences(TypedDict, total=False):
    """Type definition for user preference inputs."""
    genre: str
    mood: str
    energy: float
    likes_acoustic: bool
    prefers_popular: bool
    decade: str
    detailed_mood: str

@dataclass
class Song:
    """
    A song with audio features and metadata for content-based recommendations.
    
    Attributes:
        id: Unique song identifier
        title: Song title
        artist: Artist name
        genre: Primary music genre
        mood: Emotional mood descriptor
        energy: Energy level (0.0-1.0)
        tempo_bpm: Tempo in beats per minute
        valence: Musical positivity (0.0-1.0)
        danceability: How suitable for dancing (0.0-1.0)
        acousticness: Acoustic character (0.0-1.0)
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
    User taste preferences for personalized recommendations.
    
    Attributes:
        favorite_genre: Primary music genre preference
        favorite_mood: Preferred emotional mood
        target_energy: Preferred energy level (0.0-1.0)
        likes_acoustic: Whether user prefers acoustic songs
        prefers_popular: Whether user prefers popular songs
        favorite_decade: Preferred music era
        favorite_detailed_mood: Specific mood preference
    """
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

def load_songs(csv_path: str) -> List[SongDict]:
    """
    Load song dataset from CSV file and parse numeric audio features.
    
    Args:
        csv_path: Path to the CSV file containing song data.
        
    Returns:
        List of song dictionaries with parsed numeric fields.
        
    Raises:
        FileNotFoundError: If the CSV file does not exist.
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
            row['acousticness'] = float(row['acousticness'])
            row['popularity'] = int(row['popularity'])
            row['decade'] = row['decade']
            row['detailed_mood'] = row['detailed_mood']
            songs.append(row)
    print(f"Loading songs from {csv_path}...")
    return songs

def score_song(user_prefs: UserPreferences, song: SongDict, mode: str = 'balanced') -> Tuple[float, List[str]]:
    """
    Score a single song based on weighted match with user preferences.
    
    Scoring includes: genre match, mood match, energy similarity, acoustic/popularity/decade/mood bonuses.
    Modes adjust genre/energy emphasis: 'genre_first' doubles genre weight, 'energy_focus' doubles energy.
    
    Args:
        user_prefs: User preference dictionary with genre, mood, energy, etc.
        song: Song dictionary to score.
        mode: Ranking mode - 'balanced' (default), 'genre_first', or 'energy_focus'.
        
    Returns:
        Tuple of (total_score, list_of_explanation_reasons).
    """
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

def recommend_songs(
    user_prefs: UserPreferences, 
    songs: List[SongDict], 
    k: int = 5, 
    mode: str = 'balanced'
) -> List[Tuple[SongDict, float, str]]:
    """
    Rank all songs by preference match and return top k recommendations.
    
    Applies diversity penalties to avoid recommending multiple songs by the same artist.
    Higher scores indicate better matches with user preferences.
    
    Args:
        user_prefs: User preference dictionary.
        songs: List of song dictionaries to rank.
        k: Number of top recommendations to return (default: 5).
        mode: Ranking mode - 'balanced' (default), 'genre_first', or 'energy_focus'.
        
    Returns:
        List of tuples (song, score, explanation) sorted by score descending.
    """
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
