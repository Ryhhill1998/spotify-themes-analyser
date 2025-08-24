from src.models.db import ArtistDB
from src.models.dto import Artist


def artist_db_to_artist(db_obj: ArtistDB) -> Artist:
    return Artist(
        id=db_obj.id,
        name=db_obj.name,
        images=db_obj.images,
        spotify_url=db_obj.spotify_url,
        genres=db_obj.genres,
        followers=db_obj.followers,
        popularity=db_obj.popularity
    )
