import abc
import datetime
from typing import Annotated

from pydantic import BaseModel, Field
import pydantic

from src.models.shared import Image, TrackArtist
from src.models.enums import PositionChange, TimeRange


# -----------------------------
# Profile
# -----------------------------
class Profile(BaseModel):
    id: str
    display_name: str
    email: str | None
    images: list[Image]
    spotify_url: str
    followers: int


# -----------------------------
# Artist
# -----------------------------
class Artist(BaseModel):
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
class Track(BaseModel):
    id: str
    name: str
    images: list[Image]
    spotify_url: str
    album_name: str
    release_date: str
    explicit: bool
    duration_ms: int
    popularity: int
    artists: list[TrackArtist]


# -----------------------------
# Top Item Base
# -----------------------------
class TopItemBase(abc.ABC, BaseModel):
    user_id: str
    collection_date: datetime.date
    time_range: TimeRange
    position: int
    position_change: PositionChange | None = None

    @property
    @abc.abstractmethod
    def item_id(self) -> str: ...


# -----------------------------
# Top Artist
# -----------------------------
class TopArtist(TopItemBase):
    artist_id: str

    @property
    def item_id(self) -> str:
        return self.artist_id


# -----------------------------
# Top Track
# -----------------------------
class TopTrack(TopItemBase):
    track_id: str

    @property
    def item_id(self) -> str:
        return self.track_id


# -----------------------------
# Top Genre
# -----------------------------
class TopGenre(TopItemBase):
    genre_id: str
    percentage: float

    @property
    def item_id(self) -> str:
        return self.genre_id


# -----------------------------
# Top Emotion
# -----------------------------
class TopEmotion(TopItemBase):
    emotion_id: str
    percentage: float

    @property
    def item_id(self) -> str:
        return self.emotion_id


# -----------------------------
# Track Lyrics
# -----------------------------
class TrackLyricsRequest(BaseModel):
    track_id: str
    track_name: str
    track_artist: str


class TrackLyrics(BaseModel):
    track_id: str
    lyrics: str


# -----------------------------
# Track Emotional Profile
# -----------------------------
class TrackEmotionalProfileRequest(BaseModel):
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


class TrackEmotionalProfile(BaseModel):
    track_id: str
    emotional_profile: EmotionalProfile
