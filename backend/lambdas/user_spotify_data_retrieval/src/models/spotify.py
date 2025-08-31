from pydantic import BaseModel


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
# Profile
# -----------------------------
class SpotifyProfile(BaseModel):
    id: str
    display_name: str
    email: str | None = None
    images: list[SpotifyImage]
    external_urls: SpotifyItemExternalUrls
    followers: SpotifyProfileFollowers


# -----------------------------
# Artist
# -----------------------------
class SpotifyArtist(BaseModel):
    id: str
    name: str
    images: list[SpotifyImage]
    external_urls: SpotifyItemExternalUrls
    genres: list[str]
    followers: SpotifyProfileFollowers
    popularity: int


# -----------------------------
# Track
# -----------------------------
class SpotifyTrackAlbum(BaseModel):
    name: str
    images: list[SpotifyImage]
    release_date: str


class SpotifyTrackArtist(BaseModel):
    id: str
    name: str


class SpotifyTrack(BaseModel):
    id: str
    name: str
    album: SpotifyTrackAlbum
    external_urls: SpotifyItemExternalUrls
    explicit: bool
    duration_ms: int
    popularity: int
    artists: list[SpotifyTrackArtist]
