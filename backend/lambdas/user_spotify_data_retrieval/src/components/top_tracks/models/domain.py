from src.shared.models.domain import SpotifyImage, SpotifyItemExternalUrls
from pydantic import BaseModel


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
    artists: list[SpotifyTrackArtist]
    external_urls: SpotifyItemExternalUrls
    explicit: bool
    duration_ms: int
    popularity: int


class TopTrack(BaseModel):
    id: str
    name: str
    images: list[SpotifyImage]
    spotify_url: str
    artists: list[SpotifyTrackArtist]
    release_date: str
    album_name: str
    explicit: bool
    duration_ms: int
    popularity: int

    @classmethod
    def from_spotify_track(cls, track: SpotifyTrack, position: int | None = None) -> "TopTrack":
        return cls(
            id=track.id,
            name=track.name,
            images=track.images,
            spotify_url=track.external_urls.spotify,
            genres=track.genres,
            followers=track.followers.total,
            popularity=track.popularity,
            position=position,
        )
    