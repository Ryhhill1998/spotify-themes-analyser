from src.components.top_artists.models.db import TopArtistDB
from pydantic import BaseModel


class SpotifyImage(BaseModel):
    height: int
    width: int
    url: str


class SpotifyProfileFollowers(BaseModel):
    total: int


class SpotifyItemExternalUrls(BaseModel):
    spotify: str


class SpotifyArtist(BaseModel):
    id: str
    name: str
    images: list[SpotifyImage]
    external_urls: SpotifyItemExternalUrls
    followers: SpotifyProfileFollowers
    genres: list[str]
    popularity: int


class TopArtist(BaseModel):
    id: str
    name: str
    images: list[SpotifyImage]
    spotify_url: str
    genres: list[str]
    followers: int
    popularity: int
    position: int | None = None
    position_change: str | None = None

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
    

class PreviousTopArtist(BaseModel):
    id: str
    position: int | None = None

    @classmethod
    def from_top_artist_db(cls, top_artist_db: TopArtistDB) -> "PreviousTopArtist":
        return cls(id=top_artist_db.id, position=top_artist_db.position)
