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
    position: int | None = None
    position_change: str | None = None

    @classmethod
    def from_spotify_track(cls, track: SpotifyTrack, position: int | None = None) -> "TopTrack":
        return cls(
            id=track.id,
            name=track.name,
            images=track.album.images,
            spotify_url=track.external_urls.spotify,
            artists=track.artists,
            release_date=track.album.release_date,
            album_name=track.album.name,
            explicit=track.explicit,
            duration_ms=track.duration_ms,
            popularity=track.popularity,
            position=position,
        )
    