from src.shared.models.domain import SpotifyImage, SpotifyItemExternalUrls, SpotifyProfileFollowers, TopItem
from pydantic import BaseModel


class SpotifyArtist(BaseModel):
    id: str
    name: str
    images: list[SpotifyImage]
    external_urls: SpotifyItemExternalUrls
    followers: SpotifyProfileFollowers
    genres: list[str]
    popularity: int


class TopArtist(TopItem):
    name: str
    images: list[SpotifyImage]
    spotify_url: str
    genres: list[str]
    followers: int
    popularity: int

    @classmethod
    def from_spotify_artist(cls, artist: SpotifyArtist, position: int | None = None) -> "TopArtist":
        return cls(
            id=artist.id,
            name=artist.name,
            images=artist.images,
            spotify_url=artist.external_urls.spotify,
            genres=artist.genres,
            followers=artist.followers.total,
            popularity=artist.popularity,
            position=position,
        )
    