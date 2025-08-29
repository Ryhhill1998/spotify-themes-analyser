from dataclasses import dataclass
from datetime import date

from pydantic import BaseModel

from backend.lambdas.user_spotify_data_retrieval.src.models.enums import TimeRange


# ----------------------------- SPOTIFY ----------------------------- #
# -----------------------------
# Shared
# -----------------------------
class SpotifyImage(BaseModel):
    height: int
    width: int
    url: str


class SpotifyProfileFollowers(BaseModel):
    total: int


class SpotifyItemExternalUrls(BaseModel):
    spotify: str


# -----------------------------
# Profile API
# -----------------------------
class SpotifyProfileAPI(BaseModel):
    id: str
    display_name: str
    email: str | None
    images: list[SpotifyImage]
    href: str
    followers: SpotifyProfileFollowers


# -----------------------------
# Profile Output
# -----------------------------
class SpotifyProfile(BaseModel):
    id: str
    display_name: str
    email: str | None
    images: list[SpotifyImage]
    spotify_url: str
    followers: int


# -----------------------------
# Artist API
# -----------------------------
class SpotifyArtistAPI(BaseModel):
    id: str
    name: str
    images: list[SpotifyImage]
    external_urls: SpotifyItemExternalUrls
    genres: list[str]
    followers: SpotifyProfileFollowers
    popularity: int


# -----------------------------
# Artist Output
# -----------------------------
class SpotifyArtist(BaseModel):
    id: str
    name: str
    images: list[SpotifyImage]
    spotify_url: str
    genres: list[str]
    followers: int
    popularity: int


# -----------------------------
# Track API
# -----------------------------
class SpotifyTrackAlbum(BaseModel):
    name: str
    images: list[SpotifyImage]
    release_date: str


class SpotifyTrackArtist(BaseModel):
    id: str
    name: str


class SpotifyTrackAPI(BaseModel):
    id: str
    name: str
    album: SpotifyTrackAlbum
    external_urls: SpotifyItemExternalUrls
    explicit: bool
    duration_ms: int
    popularity: int
    artists: list[SpotifyTrackArtist]


# -----------------------------
# Track Output
# -----------------------------
class SpotifyTrack(BaseModel):
    id: str
    name: str
    images: list[SpotifyImage]
    spotify_url: str
    release_date: str
    explicit: bool
    duration_ms: int
    popularity: int
    artists: list[SpotifyTrackArtist]


# ----------------------------- TOP ITEMS ----------------------------- #
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
