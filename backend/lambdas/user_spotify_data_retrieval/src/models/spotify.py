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
    email: str | None
    images: list[SpotifyImage]
    href: str
    followers: SpotifyProfileFollowers


# # -----------------------------
# # Profile Output
# # -----------------------------
# class SpotifyProfile(BaseModel):
#     id: str
#     display_name: str
#     email: str | None
#     images: list[SpotifyImage]
#     spotify_url: str
#     followers: int


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


# # -----------------------------
# # Artist Output
# # -----------------------------
# class SpotifyArtist(BaseModel):
#     id: str
#     name: str
#     images: list[SpotifyImage]
#     spotify_url: str
#     genres: list[str]
#     followers: int
#     popularity: int


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


# # -----------------------------
# # Track Output
# # -----------------------------
# class SpotifyTrack(BaseModel):
#     id: str
#     name: str
#     images: list[SpotifyImage]
#     spotify_url: str
#     release_date: str
#     explicit: bool
#     duration_ms: int
#     popularity: int
#     artists: list[SpotifyTrackArtist]
