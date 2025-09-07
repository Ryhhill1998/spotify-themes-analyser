from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from typing import Annotated

from pydantic import BaseModel, Field

from src.models.enums import PositionChange, TimeRange


# -----------------------------
# Shared
# -----------------------------
@dataclass
class Image:
    height: int
    width: int
    url: str


# -----------------------------
# Profile
# -----------------------------
@dataclass
class Profile:
    id: str
    display_name: str
    email: str | None
    images: list[Image]
    spotify_url: str
    followers: int


# -----------------------------
# Artist
# -----------------------------
@dataclass
class Artist:
    id: str
    name: str
    images: list[Image]
    spotify_url: str
    genres: list[str]
    followers: int
    popularity: int


# -----------------------------
# Track
# -----------------------------
@dataclass
class Track:
    id: str
    name: str
    images: list[Image]
    spotify_url: str
    album_name: str
    release_date: str
    explicit: bool
    duration_ms: int
    popularity: int
    artist_ids: list[str]


# -----------------------------
# Top Item Base
# -----------------------------
@dataclass(kw_only=True)
class TopItemBase(ABC):
    user_id: str
    collection_date: date
    time_range: TimeRange
    position: int
    position_change: PositionChange | None = None

    @property
    @abstractmethod
    def item_id(self) -> str:...


# -----------------------------
# Top Artist
# -----------------------------
@dataclass(kw_only=True)
class TopArtist(TopItemBase):
    artist_id: str

    @property
    def item_id(self) -> str:
        return self.artist_id


# -----------------------------
# Top Track
# -----------------------------
@dataclass(kw_only=True)
class TopTrack(TopItemBase):
    track_id: str

    @property
    def item_id(self) -> str:
        return self.track_id


# -----------------------------
# Top Genre
# -----------------------------
@dataclass(kw_only=True)
class TopGenre(TopItemBase):
    genre_id: str
    percentage: float

    @property
    def item_id(self) -> str:
        return self.genre_id


# -----------------------------
# Top Emotion
# -----------------------------
@dataclass(kw_only=True)
class TopEmotion(TopItemBase):
    emotion_id: str
    percentage: float

    @property
    def item_id(self) -> str:
        return self.emotion_id
    

@dataclass
class LyricsRequest:
    track_id: str
    track_name: str
    track_artist: str


class TrackLyrics(BaseModel):
    track_id: str
    lyrics: str


@dataclass
class EmotionalProfileRequest:
    track_id: str
    lyrics: str


EmotionPercentage = Annotated[float, Field(ge=0, le=1)]


class EmotionalProfile(BaseModel):
    joy: EmotionPercentage
    sadness: EmotionPercentage
    anger: EmotionPercentage
    fear: EmotionPercentage
    love: EmotionPercentage
    hope: EmotionPercentage
    nostalgia: EmotionPercentage
    loneliness: EmotionPercentage
    confidence: EmotionPercentage
    despair: EmotionPercentage
    excitement: EmotionPercentage
    mystery: EmotionPercentage
    defiance: EmotionPercentage
    gratitude: EmotionPercentage
    spirituality: EmotionPercentage


@dataclass
class TrackEmotionalProfile:
    track_id: str
    emotional_profile: EmotionalProfile
