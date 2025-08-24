from src.models.dto import Artist, TopArtist
from src.models.db import ArtistDB, TopArtistDB

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


def top_artist_to_top_artist_db(top_artist: TopArtist) -> TopArtistDB:
    return TopArtistDB(
        user_id=top_artist.user_id,
        artist_id=top_artist.artist_id,
        collection_date=top_artist.collection_date,
        time_range=top_artist.time_range,
        position=top_artist.position,
        position_change=top_artist.position_change,
    )
