from dataclasses import dataclass
from datetime import date

from src.models.enums import TimeRange


# -----------------------------
# Profile
# -----------------------------
@dataclass
class Profile:
    id: str
    display_name: str
    email: str | None
    images: list[dict]
    spotify_url: str
    followers: int


# -----------------------------
# Artist
# -----------------------------
@dataclass
class Artist:
    id: str
    name: str
    images: list[dict]
    spotify_url: str
    genres: list[str]
    followers: int
    popularity: int


# -----------------------------
# Top Item Base
# -----------------------------
@dataclass
class TopItemBase:
    id: int | None  # None if it hasn’t been stored in DB yet
    user_id: str
    time_range: TimeRange
    collection_date: date
    position: int
    position_change: int | None = None


# -----------------------------
# Top Artist
# -----------------------------
@dataclass
class TopArtist(TopItemBase):
    artist_id: str


# -----------------------------
# Track
# -----------------------------
@dataclass
class Track:
    id: str
    name: str
    images: list[dict]
    spotify_url: str
    release_date: str
    explicit: bool
    duration_ms: int
    popularity: int
    artists: list[dict]  # list of {"id": str, "name": str}


# -----------------------------
# Top Track
# -----------------------------
@dataclass
class TopTrack(TopItemBase):
    track_id: str


# -----------------------------
# Top Genre
# -----------------------------
@dataclass
class TopGenre(TopItemBase):
    genre_id: str
    percentage: float


# -----------------------------
# Top Emotion
# -----------------------------
@dataclass
class TopEmotion(TopItemBase):
    emotion_id: str
    percentage: float


# -----------------------------
# Lyrics (from lyrics service)
# -----------------------------
@dataclass
class Lyrics:
    track_id: str
    lyrics: str
    source_url: str | None = None


# -----------------------------
# Emotional Profile (from model)
# -----------------------------
@dataclass
class EmotionScore:
    emotion: str
    score: float


@dataclass
class EmotionalProfile:
    track_id: str
    scores: list[EmotionScore]
