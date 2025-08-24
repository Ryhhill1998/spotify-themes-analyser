from src.models.db import ArtistDB, TopArtistDB, TopTrackDB
from src.models.dto import Artist, TopArtist, TopTrack


def artist_db_to_artist(db_artist: ArtistDB) -> Artist:
    return Artist(
        id=db_artist.id,
        name=db_artist.name,
        images=db_artist.images,
        spotify_url=db_artist.spotify_url,
        genres=db_artist.genres,
        followers=db_artist.followers,
        popularity=db_artist.popularity
    )


def top_artist_db_to_top_artist(db_top_artist: TopArtistDB) -> TopArtist:
    return TopArtist(
        id=db_top_artist.id,
        user_id=db_top_artist.user_id,
        artist_id=db_top_artist.artist_id,
        collection_date=db_top_artist.collection_date,
        time_range=db_top_artist.time_range,
        position=db_top_artist.position,
        position_change=db_top_artist.position_change,
    )


def top_track_db_to_top_track(db_top_track: TopTrackDB) -> TopTrack:
    return TopTrack(
        id=db_top_track.id,
        user_id=db_top_track.user_id,
        track_id=db_top_track.track_id,
        collection_date=db_top_track.collection_date,
        time_range=db_top_track.time_range,
        position=db_top_track.position,
        position_change=db_top_track.position_change,
    )
