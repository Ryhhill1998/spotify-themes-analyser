from pydantic import BaseModel

from src.models.shared import Image, TrackArtist


# -----------------------------
# Shared
# -----------------------------
class SpotifyProfileFollowers(BaseModel):
    total: int


class SpotifyItemExternalUrls(BaseModel):
    spotify: str


# -----------------------------
# Profile
# -----------------------------
class SpotifyProfile(BaseModel):
    id: str
    display_name: str
    email: str | None = None
    images: list[Image]
    external_urls: SpotifyItemExternalUrls
    followers: SpotifyProfileFollowers


# -----------------------------
# Artist
# -----------------------------
class SpotifyArtist(BaseModel):
    id: str
    name: str
    images: list[Image]
    external_urls: SpotifyItemExternalUrls
    genres: list[str]
    followers: SpotifyProfileFollowers
    popularity: int


# -----------------------------
# Track
# -----------------------------
class SpotifyTrackAlbum(BaseModel):
    name: str
    images: list[Image]
    release_date: str


class SpotifyTrack(BaseModel):
    id: str
    name: str
    album: SpotifyTrackAlbum
    external_urls: SpotifyItemExternalUrls
    explicit: bool
    duration_ms: int
    popularity: int
    artists: list[TrackArtist]
