from dataclasses import dataclass
from datetime import date

from src.models.enums import PositionChange, TimeRange


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
# Track
# -----------------------------
@dataclass
class TrackArtist:
    id: str
    name: str

    
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
    artists: list[TrackArtist]


@dataclass
class EnrichedTrack:
    id: str
    name: str
    images: list[dict]
    spotify_url: str
    release_date: str
    explicit: bool
    duration_ms: int
    popularity: int
    artists: list[Artist]


# -----------------------------
# Top Item Base
# -----------------------------
@dataclass
class TopItemBase:
    user_id: str
    time_range: TimeRange
    collection_date: date
    position: int
    position_change: PositionChange | None

    def unique_id(self) -> str:
        raise NotImplementedError


# -----------------------------
# Top Artist
# -----------------------------
@dataclass
class TopArtist(TopItemBase):
    artist_id: str

    def unique_id(self) -> str:
        return self.artist_id


# -----------------------------
# Top Track
# -----------------------------
@dataclass
class TopTrack(TopItemBase):
    track_id: str

    def unique_id(self) -> str:
        return self.track_id


# -----------------------------
# Top Genre
# -----------------------------
@dataclass
class TopGenre(TopItemBase):
    genre_id: str
    percentage: float

    def unique_id(self) -> str:
        return self.genre_id


# -----------------------------
# Top Emotion
# -----------------------------
@dataclass
class TopEmotion(TopItemBase):
    emotion_id: str
    percentage: float

    def unique_id(self) -> str:
        return self.emotion_id


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
