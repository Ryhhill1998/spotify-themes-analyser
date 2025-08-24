from src.models.dto import Artist
from src.models.db import ArtistDB

def artist_to_artist_db(artist: Artist) -> ArtistDB:
    return ArtistDB(
        id=artist.id,
        name=artist.name,
        images=artist.images,
        spotify_url=artist.spotify_url,
        genres=artist.genres,
        followers=artist.followers,
        popularity=artist.popularity
    )
