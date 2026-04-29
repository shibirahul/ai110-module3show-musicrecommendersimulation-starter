from __future__ import annotations

import csv
import logging
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple, TypedDict


LOGGER = logging.getLogger("vibematcher")
SUPPORTED_MODES = {"balanced", "genre_first", "energy_focus"}
TOKEN_RE = re.compile(r"[a-z0-9']+")
STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "for",
    "from",
    "i",
    "in",
    "is",
    "it",
    "me",
    "my",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "with",
}


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

    The optional defaults keep the Module 3 starter tests compatible while the
    dictionary-based pipeline uses the expanded dataset fields.
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
    popularity: int = 0
    decade: str = ""
    detailed_mood: str = ""


@dataclass
class UserProfile:
    """User taste preferences for personalized recommendations."""

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool = False
    prefers_popular: bool = False
    favorite_decade: str = ""
    favorite_detailed_mood: str = ""


@dataclass(frozen=True)
class IntentContext:
    """Retrieved knowledge record that maps a listening goal to music signals."""

    id: str
    name: str
    keywords: Tuple[str, ...]
    preferred_genres: Tuple[str, ...]
    preferred_moods: Tuple[str, ...]
    target_energy: float
    detailed_moods: Tuple[str, ...]
    decades: Tuple[str, ...]
    likes_acoustic: bool
    prefers_popular: bool
    rationale: str
    guardrail: str
    score: float = 0.0
    matched_terms: Tuple[str, ...] = ()


@dataclass(frozen=True)
class ResponseStyle:
    """Few-shot style record for constrained recommendation responses."""

    id: str
    label: str
    tone_rules: str
    example_input: str
    baseline_example: str
    specialized_example: str


class Recommender:
    """Dataclass-friendly wrapper around the dictionary recommendation engine."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Score and rank songs by user preference match."""

        song_dicts = [_song_to_dict(song) for song in self.songs]
        preferences = _profile_to_preferences(user)
        ranked = recommend_songs(preferences, song_dicts, k=k, mode="balanced")
        songs_by_id = {song.id: song for song in self.songs}
        return [songs_by_id[item[0]["id"]] for item in ranked]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Generate a transparent explanation for why a song was recommended."""

        score, reasons = score_song(_profile_to_preferences(user), _song_to_dict(song))
        return f"Score {score:.2f}: {', '.join(reasons)}"


def configure_logging(log_path: str = "logs/recommender.log") -> None:
    """Configure lightweight file logging for runs, guardrails, and evaluation."""

    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    LOGGER.setLevel(logging.INFO)

    resolved = str(path.resolve())
    for handler in LOGGER.handlers:
        if isinstance(handler, logging.FileHandler) and handler.baseFilename == resolved:
            return

    handler = logging.FileHandler(path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    LOGGER.addHandler(handler)


def load_songs(csv_path: str) -> List[SongDict]:
    """
    Load song dataset from CSV file and parse numeric audio features.

    Args:
        csv_path: Path to the CSV file containing song data.

    Returns:
        List of song dictionaries with parsed numeric fields.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        ValueError: If a numeric field cannot be parsed.
    """

    songs: List[SongDict] = []
    with open(csv_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            song: SongDict = {
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"].strip().lower(),
                "mood": row["mood"].strip().lower(),
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
                "popularity": int(row["popularity"]),
                "decade": row["decade"].strip(),
                "detailed_mood": row["detailed_mood"].strip().lower(),
            }
            songs.append(song)

    LOGGER.info("loaded_songs path=%s count=%s", csv_path, len(songs))
    return songs


def load_intent_contexts(csv_path: str) -> List[IntentContext]:
    """Load retrieval knowledge records used by the offline RAG workflow."""

    contexts: List[IntentContext] = []
    with open(csv_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            contexts.append(
                IntentContext(
                    id=row["id"].strip(),
                    name=row["name"].strip(),
                    keywords=tuple(_split_pipe_list(row["keywords"])),
                    preferred_genres=tuple(_split_pipe_list(row["preferred_genres"])),
                    preferred_moods=tuple(_split_pipe_list(row["preferred_moods"])),
                    target_energy=float(row["target_energy"]),
                    detailed_moods=tuple(_split_pipe_list(row["detailed_moods"])),
                    decades=tuple(_split_pipe_list(row["decades"])),
                    likes_acoustic=_parse_bool(row["likes_acoustic"]),
                    prefers_popular=_parse_bool(row["prefers_popular"]),
                    rationale=row["rationale"].strip(),
                    guardrail=row["guardrail"].strip(),
                )
            )

    LOGGER.info("loaded_intent_contexts path=%s count=%s", csv_path, len(contexts))
    return contexts


def load_response_styles(csv_path: str) -> List[ResponseStyle]:
    """Load synthetic few-shot response styles for specialization demos."""

    styles: List[ResponseStyle] = []
    with open(csv_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            styles.append(
                ResponseStyle(
                    id=row["id"].strip(),
                    label=row["label"].strip(),
                    tone_rules=row["tone_rules"].strip(),
                    example_input=row["example_input"].strip(),
                    baseline_example=row["baseline_example"].strip(),
                    specialized_example=row["specialized_example"].strip(),
                )
            )

    LOGGER.info("loaded_response_styles path=%s count=%s", csv_path, len(styles))
    return styles


def retrieve_intent_contexts(
    query: str,
    contexts: Sequence[IntentContext],
    limit: int = 3,
) -> List[IntentContext]:
    """
    Retrieve listening-intent records before recommending songs.

    This is an offline RAG step: the user's natural-language goal is matched
    against a small curated knowledge base, and the retrieved records directly
    influence preference planning and final ranking.
    """

    query_tokens = set(_tokenize(query))
    if not query_tokens:
        return []

    ranked: List[IntentContext] = []
    for context in contexts:
        document_text = " ".join(
            [
                context.name,
                " ".join(context.keywords),
                " ".join(context.preferred_genres),
                " ".join(context.preferred_moods),
                " ".join(context.detailed_moods),
                context.rationale,
            ]
        )
        document_tokens = set(_tokenize(document_text))
        matched = tuple(sorted(query_tokens.intersection(document_tokens)))
        if not matched:
            continue

        coverage = len(matched) / max(1, len(query_tokens))
        precision = len(matched) / max(1, len(document_tokens))
        score = min(1.0, (0.85 * coverage) + (0.15 * math.sqrt(precision)))
        ranked.append(
            IntentContext(
                **{
                    **context.__dict__,
                    "score": round(score, 3),
                    "matched_terms": matched,
                }
            )
        )

    ranked.sort(key=lambda item: item.score, reverse=True)
    return ranked[:limit]


def score_song(
    user_prefs: UserPreferences,
    song: SongDict,
    mode: str = "balanced",
) -> Tuple[float, List[str]]:
    """
    Score a single song based on weighted matches with user preferences.

    Modes adjust genre/energy emphasis: `genre_first` doubles genre weight, and
    `energy_focus` doubles energy similarity weight.
    """

    safe_mode = mode if mode in SUPPORTED_MODES else "balanced"
    score = 0.0
    reasons: List[str] = []

    genre_weight = 2.0
    mood_weight = 1.0
    energy_weight = 1.0

    if safe_mode == "genre_first":
        genre_weight *= 2
        reasons.append("genre-first mode")
    elif safe_mode == "energy_focus":
        energy_weight *= 2
        reasons.append("energy-focus mode")

    if song["genre"] == user_prefs.get("genre"):
        score += genre_weight
        reasons.append(f"genre match (+{genre_weight:.1f})")

    if song["mood"] == user_prefs.get("mood"):
        score += mood_weight
        reasons.append(f"mood match (+{mood_weight:.1f})")

    energy_diff = abs(song["energy"] - float(user_prefs.get("energy", 0.5)))
    energy_sim = max(0.0, 1.0 - energy_diff) * energy_weight
    score += energy_sim
    reasons.append(f"energy similarity (+{energy_sim:.2f})")

    if user_prefs.get("likes_acoustic", False) and song["acousticness"] > 0.7:
        score += 0.5
        reasons.append("acoustic preference (+0.5)")

    if user_prefs.get("prefers_popular", False) and song["popularity"] > 80:
        score += 0.5
        reasons.append("popularity preference (+0.5)")

    if song["decade"] == user_prefs.get("decade"):
        score += 0.5
        reasons.append("decade match (+0.5)")

    if song["detailed_mood"] == user_prefs.get("detailed_mood"):
        score += 0.5
        reasons.append("detailed mood match (+0.5)")

    return score, reasons


def recommend_songs(
    user_prefs: UserPreferences,
    songs: List[SongDict],
    k: int = 5,
    mode: str = "balanced",
    retrieved_contexts: Optional[Sequence[IntentContext]] = None,
) -> List[Tuple[SongDict, float, str]]:
    """
    Rank all songs by preference match and return top k recommendations.

    Applies a diversity penalty to avoid repeated artists and, when retrieved
    contexts are provided, adds a small context-fit bonus so RAG changes the
    ranking instead of being displayed as separate metadata only.
    """

    scored_songs: List[Tuple[SongDict, float, str]] = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, mode)
        context_bonus, context_reason = score_context_fit(song, retrieved_contexts or [])
        if context_bonus:
            score += context_bonus
            reasons.append(context_reason)
        scored_songs.append((song, score, ", ".join(reasons)))

    scored_songs.sort(key=lambda item: item[1], reverse=True)

    adjusted: List[Tuple[SongDict, float, str]] = []
    seen_artists: set[str] = set()
    for song, score, explanation in scored_songs:
        if song["artist"] in seen_artists:
            score -= 0.5
            explanation = f"{explanation}, diversity penalty (-0.5)"
        else:
            seen_artists.add(song["artist"])
        adjusted.append((song, score, explanation))

    adjusted.sort(key=lambda item: item[1], reverse=True)
    return adjusted[: max(1, k)]


def score_context_fit(
    song: SongDict,
    contexts: Sequence[IntentContext],
) -> Tuple[float, str]:
    """Score whether a song fits retrieved listening-intent records."""

    if not contexts:
        return 0.0, ""

    bonus = 0.0
    context_names: List[str] = []
    for context in contexts[:2]:
        context_bonus = 0.0
        weight = 0.5 + (min(1.0, context.score) * 0.5)
        if song["genre"] in context.preferred_genres:
            context_bonus += 0.30 * weight
        if song["mood"] in context.preferred_moods:
            context_bonus += 0.25 * weight
        if song["detailed_mood"] in context.detailed_moods:
            context_bonus += 0.20 * weight
        if song["decade"] in context.decades:
            context_bonus += 0.10 * weight

        energy_fit = max(0.0, 1.0 - abs(song["energy"] - context.target_energy))
        context_bonus += 0.20 * energy_fit * weight

        if context.likes_acoustic and song["acousticness"] > 0.7:
            context_bonus += 0.15 * weight
        if context.prefers_popular and song["popularity"] > 80:
            context_bonus += 0.15 * weight

        if context_bonus:
            bonus += context_bonus
            context_names.append(context.name)

    if not bonus:
        return 0.0, ""
    return round(bonus, 2), f"retrieved context fit: {', '.join(context_names)} (+{bonus:.2f})"


def run_recommendation_workflow(
    intent_text: str,
    songs: List[SongDict],
    user_prefs: Optional[UserPreferences] = None,
    contexts: Optional[Sequence[IntentContext]] = None,
    k: int = 5,
    mode: str = "balanced",
    lock_explicit_preferences: bool = False,
) -> Dict[str, object]:
    """
    Execute the end-to-end applied AI workflow.

    Steps:
    1. Retrieve relevant listening-intent guidance.
    2. Validate and plan final preferences with guardrails.
    3. Score and rerank songs with retrieved context.
    4. Estimate confidence, log the run, and return observable steps.
    """

    warnings: List[str] = []
    safe_mode = mode if mode in SUPPORTED_MODES else "balanced"
    if safe_mode != mode:
        warnings.append(f"Unknown mode '{mode}' was replaced with 'balanced'.")

    bounded_k = max(1, min(10, int(k)))
    if bounded_k != k:
        warnings.append("Recommendation count was limited to the supported range of 1 to 10.")

    if contexts is None:
        context_path = Path(__file__).resolve().parent.parent / "data" / "intent_guides.csv"
        contexts = load_intent_contexts(str(context_path))

    retrieved = retrieve_intent_contexts(intent_text, contexts)
    if intent_text.strip() and not retrieved:
        warnings.append("No matching listening guide was retrieved; using validated preferences only.")

    planned_preferences, planning_steps, planning_warnings = plan_preferences(
        user_prefs or {},
        songs,
        retrieved,
        lock_explicit_preferences=lock_explicit_preferences,
    )
    warnings.extend(planning_warnings)
    warnings.extend(_safety_warnings(intent_text))

    recommendations = recommend_songs(
        planned_preferences,
        songs,
        k=bounded_k,
        mode=safe_mode,
        retrieved_contexts=retrieved,
    )
    confidence = estimate_confidence(recommendations, retrieved, safe_mode, bool(intent_text.strip()))
    if confidence < 0.55:
        warnings.append("Low confidence: provide a clearer goal or expand the song catalog.")

    plan_steps = [
        f"Parsed listening goal: {intent_text.strip() or 'no free-text goal provided'}",
        _retrieval_step_summary(retrieved),
        *planning_steps,
        f"Scored {len(songs)} songs with {safe_mode} mode and context-aware reranking.",
        f"Estimated confidence: {confidence:.2f}",
    ]

    LOGGER.info(
        "workflow_run intent=%r mode=%s top_k=%s confidence=%.2f warnings=%s top_song=%s",
        intent_text,
        safe_mode,
        bounded_k,
        confidence,
        len(warnings),
        recommendations[0][0]["title"] if recommendations else "none",
    )

    result: Dict[str, object] = {
        "intent_text": intent_text,
        "mode": safe_mode,
        "top_k": bounded_k,
        "preferences": planned_preferences,
        "retrieved_contexts": retrieved,
        "recommendations": recommendations,
        "confidence": confidence,
        "warnings": warnings,
        "plan_steps": plan_steps,
    }
    result["baseline_response"] = generate_baseline_response(result)
    result["specialized_response"] = generate_specialized_response(result)
    result["specialization_metrics"] = compare_response_specialization(result)
    return result


def generate_baseline_response(workflow_result: Dict[str, object]) -> str:
    """Generate a deliberately minimal baseline response for comparison."""

    recommendations = workflow_result["recommendations"]
    if not recommendations:
        return "No recommendation available."

    top_song, score, _explanation = recommendations[0]
    return f"Top recommendation: {top_song['title']} by {top_song['artist']} with score {score:.2f}."


def generate_specialized_response(
    workflow_result: Dict[str, object],
    style: Optional[ResponseStyle] = None,
) -> str:
    """
    Generate a constrained specialist response from workflow evidence.

    The output follows the few-shot style target used in
    `data/response_styles.csv`: concise, evidence-backed, and explicit about
    confidence and guardrails.
    """

    recommendations = workflow_result["recommendations"]
    if not recommendations:
        return "Recommendation brief: no songs were available to rank."

    top_song, score, explanation = recommendations[0]
    retrieved = workflow_result["retrieved_contexts"]
    warnings = workflow_result["warnings"]
    confidence = workflow_result["confidence"]

    style_label = style.label if style else "Evidence-backed music advisor"
    intent = str(workflow_result.get("intent_text") or "structured preference request")
    retrieved_name = retrieved[0].name if retrieved else "no retrieved guide"
    retrieved_score = f"{retrieved[0].score:.2f}" if retrieved else "0.00"
    warning_text = " ".join(warnings) if warnings else "No guardrail warnings were triggered."

    next_listens = []
    for index, (song, item_score, _reason) in enumerate(recommendations[1:3], start=2):
        next_listens.append(f"{index}. {song['title']} by {song['artist']} ({item_score:.2f})")
    next_listens_text = "; ".join(next_listens) if next_listens else "No backup tracks were requested."

    return (
        f"Recommendation brief ({style_label}): {intent}\n"
        f"Best match: {top_song['title']} by {top_song['artist']} ({top_song['genre']}, "
        f"score {score:.2f}).\n"
        f"Evidence: retrieved guide '{retrieved_name}' scored {retrieved_score}; ranking reasons were "
        f"{explanation}.\n"
        f"Next listens: {next_listens_text}.\n"
        f"Confidence: {confidence:.2f}.\n"
        f"Reliability note: {warning_text}"
    )


def compare_response_specialization(
    workflow_result: Dict[str, object],
    style: Optional[ResponseStyle] = None,
) -> Dict[str, object]:
    """Compare baseline and specialized response behavior with simple metrics."""

    baseline = generate_baseline_response(workflow_result)
    specialized = generate_specialized_response(workflow_result, style=style)
    baseline_metrics = _response_metrics(baseline)
    specialized_metrics = _response_metrics(specialized)

    return {
        "baseline": baseline,
        "specialized": specialized,
        "baseline_metrics": baseline_metrics,
        "specialized_metrics": specialized_metrics,
        "evidence_marker_delta": specialized_metrics["evidence_markers"]
        - baseline_metrics["evidence_markers"],
        "word_count_delta": specialized_metrics["word_count"] - baseline_metrics["word_count"],
    }


def plan_preferences(
    user_prefs: UserPreferences,
    songs: Sequence[SongDict],
    retrieved_contexts: Sequence[IntentContext],
    lock_explicit_preferences: bool = False,
) -> Tuple[UserPreferences, List[str], List[str]]:
    """Create final recommendation preferences from explicit inputs and RAG context."""

    warnings: List[str] = []
    available = _available_values(songs)
    fallback = _fallback_preferences(songs)
    context_preferences = _context_preferences(retrieved_contexts, available)
    final: UserPreferences = {}

    context_first = bool(retrieved_contexts) and not lock_explicit_preferences
    order_note = "retrieved context first" if context_first else "explicit preferences first"

    for key in ("genre", "mood", "decade", "detailed_mood"):
        explicit_value = _clean_text(user_prefs.get(key))
        context_value = context_preferences.get(key)
        candidates = (
            [context_value, explicit_value, fallback[key]]
            if context_first
            else [explicit_value, context_value, fallback[key]]
        )
        chosen = _first_valid(candidates, available[key])
        if explicit_value and explicit_value not in available[key]:
            warnings.append(f"Unsupported {key} '{explicit_value}' was ignored.")
        final[key] = chosen

    explicit_energy, energy_warning = _clean_energy(user_prefs.get("energy"))
    if energy_warning:
        warnings.append(energy_warning)
    context_energy = context_preferences.get("energy")

    if context_first and context_energy is not None:
        if explicit_energy is None:
            final["energy"] = context_energy
        else:
            final["energy"] = round((0.7 * float(context_energy)) + (0.3 * explicit_energy), 2)
    elif explicit_energy is not None:
        final["energy"] = explicit_energy
    elif context_energy is not None:
        final["energy"] = float(context_energy)
    else:
        final["energy"] = float(fallback["energy"])

    for key in ("likes_acoustic", "prefers_popular"):
        explicit_bool = _clean_bool(user_prefs.get(key))
        context_bool = context_preferences.get(key)
        if context_first and context_bool is not None:
            final[key] = bool(context_bool)
        elif explicit_bool is not None:
            final[key] = explicit_bool
        elif context_bool is not None:
            final[key] = bool(context_bool)
        else:
            final[key] = bool(fallback[key])

    steps = [
        f"Planned preferences using {order_note}: "
        f"genre={final['genre']}, mood={final['mood']}, energy={final['energy']:.2f}, "
        f"decade={final['decade']}, detailed_mood={final['detailed_mood']}.",
        "Applied guardrails for valid catalog values, boolean preferences, and 0.0-1.0 energy bounds.",
    ]
    return final, steps, warnings


def estimate_confidence(
    recommendations: Sequence[Tuple[SongDict, float, str]],
    retrieved_contexts: Sequence[IntentContext],
    mode: str,
    has_intent: bool,
) -> float:
    """Estimate confidence from match score, retrieval quality, and diversity."""

    if not recommendations:
        return 0.0

    top_score = max(0.0, recommendations[0][1])
    max_score = 6.3
    if mode == "genre_first":
        max_score = 8.3
    elif mode == "energy_focus":
        max_score = 7.3

    score_component = min(1.0, top_score / max_score)
    if retrieved_contexts:
        retrieval_component = min(1.0, retrieved_contexts[0].score)
    else:
        retrieval_component = 0.55 if has_intent else 0.65

    unique_artists = len({item[0]["artist"] for item in recommendations})
    diversity_component = unique_artists / max(1, len(recommendations))
    confidence = (0.55 * score_component) + (0.30 * retrieval_component) + (0.15 * diversity_component)
    return round(max(0.0, min(1.0, confidence)), 2)


def _song_to_dict(song: Song) -> SongDict:
    return {
        "id": song.id,
        "title": song.title,
        "artist": song.artist,
        "genre": song.genre,
        "mood": song.mood,
        "energy": song.energy,
        "tempo_bpm": song.tempo_bpm,
        "valence": song.valence,
        "danceability": song.danceability,
        "acousticness": song.acousticness,
        "popularity": song.popularity,
        "decade": song.decade,
        "detailed_mood": song.detailed_mood,
    }


def _profile_to_preferences(user: UserProfile) -> UserPreferences:
    return {
        "genre": _clean_text(user.favorite_genre),
        "mood": _clean_text(user.favorite_mood),
        "energy": max(0.0, min(1.0, user.target_energy)),
        "likes_acoustic": user.likes_acoustic,
        "prefers_popular": user.prefers_popular,
        "decade": user.favorite_decade,
        "detailed_mood": _clean_text(user.favorite_detailed_mood),
    }


def _tokenize(text: str) -> List[str]:
    return [token for token in TOKEN_RE.findall(text.lower()) if token not in STOP_WORDS]


def _response_metrics(response_text: str) -> Dict[str, int]:
    tokens = _tokenize(response_text)
    lower_text = response_text.lower()
    evidence_terms = (
        "evidence",
        "retrieved guide",
        "ranking reasons",
        "confidence",
        "reliability note",
        "guardrail",
        "warning",
    )
    return {
        "word_count": len(tokens),
        "evidence_markers": sum(1 for term in evidence_terms if term in lower_text),
        "line_count": len([line for line in response_text.splitlines() if line.strip()]),
    }


def _split_pipe_list(value: str) -> List[str]:
    return [item.strip().lower() for item in value.split("|") if item.strip()]


def _parse_bool(value: object) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _clean_bool(value: object) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y"}:
        return True
    if text in {"0", "false", "no", "n"}:
        return False
    return None


def _clean_text(value: object) -> str:
    return str(value).strip().lower() if value is not None else ""


def _clean_energy(value: object) -> Tuple[Optional[float], Optional[str]]:
    if value is None or value == "":
        return None, None
    try:
        energy = float(value)
    except (TypeError, ValueError):
        return None, f"Invalid energy '{value}' was replaced with a fallback value."

    clamped = max(0.0, min(1.0, energy))
    if clamped != energy:
        return clamped, "Energy was clamped to the supported 0.0-1.0 range."
    return clamped, None


def _available_values(songs: Sequence[SongDict]) -> Dict[str, set[str]]:
    return {
        "genre": {song["genre"] for song in songs},
        "mood": {song["mood"] for song in songs},
        "decade": {song["decade"] for song in songs},
        "detailed_mood": {song["detailed_mood"] for song in songs},
    }


def _fallback_preferences(songs: Sequence[SongDict]) -> UserPreferences:
    if not songs:
        return {
            "genre": "pop",
            "mood": "happy",
            "energy": 0.6,
            "likes_acoustic": False,
            "prefers_popular": False,
            "decade": "2020s",
            "detailed_mood": "upbeat",
        }

    def most_common(values: Iterable[str], preferred: str) -> str:
        counts = Counter(values)
        if preferred in counts:
            return preferred
        return counts.most_common(1)[0][0]

    return {
        "genre": most_common((song["genre"] for song in songs), "pop"),
        "mood": most_common((song["mood"] for song in songs), "happy"),
        "energy": round(sum(song["energy"] for song in songs) / len(songs), 2),
        "likes_acoustic": False,
        "prefers_popular": False,
        "decade": most_common((song["decade"] for song in songs), "2020s"),
        "detailed_mood": most_common((song["detailed_mood"] for song in songs), "upbeat"),
    }


def _context_preferences(
    contexts: Sequence[IntentContext],
    available: Dict[str, set[str]],
) -> UserPreferences:
    if not contexts:
        return {}

    context = contexts[0]
    preferences: UserPreferences = {}
    genre = _first_valid(context.preferred_genres, available["genre"])
    mood = _first_valid(context.preferred_moods, available["mood"])
    decade = _first_valid(context.decades, available["decade"])
    detailed_mood = _first_valid(context.detailed_moods, available["detailed_mood"])

    if genre:
        preferences["genre"] = genre
    if mood:
        preferences["mood"] = mood
    if decade:
        preferences["decade"] = decade
    if detailed_mood:
        preferences["detailed_mood"] = detailed_mood
    preferences["energy"] = max(0.0, min(1.0, context.target_energy))
    preferences["likes_acoustic"] = context.likes_acoustic
    preferences["prefers_popular"] = context.prefers_popular
    return preferences


def _first_valid(candidates: Iterable[object], valid_values: set[str]) -> str:
    for candidate in candidates:
        value = _clean_text(candidate)
        if value in valid_values:
            return value
    return sorted(valid_values)[0] if valid_values else ""


def _retrieval_step_summary(retrieved: Sequence[IntentContext]) -> str:
    if not retrieved:
        return "Retrieved 0 listening guides."

    guide_summaries = []
    for context in retrieved:
        matches = ", ".join(context.matched_terms) if context.matched_terms else "no shared terms"
        guide_summaries.append(f"{context.name} ({context.score:.2f}; matched {matches})")
    return f"Retrieved {len(retrieved)} listening guide(s): " + "; ".join(guide_summaries)


def _safety_warnings(intent_text: str) -> List[str]:
    text = intent_text.lower()
    warnings: List[str] = []
    if any(term in text for term in ("depressed", "depression", "panic", "self harm", "suicide")):
        warnings.append(
            "Safety note: this recommender can suggest music, but it is not mental health or crisis support."
        )
    if any(term in text for term in ("race", "religion", "gender", "disability")):
        warnings.append(
            "Sensitive-attribute guardrail: recommendations are based on listening context, not protected traits."
        )
    return warnings
