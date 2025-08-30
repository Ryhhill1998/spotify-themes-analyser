from dataclasses import dataclass
from datetime import date

from backend.lambdas.user_spotify_data_retrieval.src.models.enums import TimeRange


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
@dataclass
class TopItem:
    user_id: str
    item_id: str
    collection_date: date
    time_range: TimeRange
    position: int
    position_change: int | None = None


# -----------------------------
# Top Artist
# -----------------------------
@dataclass
class TopArtist(TopItem):
    artist_id: str

    @property
    def item_id(self) -> str:
        return self.artist_id


# -----------------------------
# Top Track
# -----------------------------
@dataclass
class TopTrack(TopItem):
    track_id: str

    @property
    def item_id(self) -> str:
        return self.track_id


# -----------------------------
# Top Genre
# -----------------------------
@dataclass
class TopGenre(TopItem):
    genre_id: str
    percentage: float

    @property
    def item_id(self) -> str:
        return self.genre_id


# -----------------------------
# Top Emotion
# -----------------------------
@dataclass
class TopEmotion(TopItem):
    emotion_id: str
    percentage: float

    @property
    def item_id(self) -> str:
        return self.emotion_id
