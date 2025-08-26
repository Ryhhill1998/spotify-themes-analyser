from src.models.dto import Artist, EnrichedTrack, TopArtist
from src.models.db import ArtistDB, ProfileDB, TopArtistDB, TopTrackDB, TrackDB


def profile_to_profile_db(profile) -> ProfileDB:
    return ProfileDB(
        id=profile.id,
        display_name=profile.display_name,
        email=profile.email,
        images=profile.images,
        spotify_url=profile.spotify_url,
        followers=profile.followers,
    )


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


def track_to_track_db(track: EnrichedTrack, db_artists: list[ArtistDB]) -> TrackDB:
    return TrackDB(
        id=track.id,
        name=track.name,
        images=track.images,
        spotify_url=track.spotify_url,
        release_date=track.release_date,
        explicit=track.explicit,
        duration_ms=track.duration_ms,
        popularity=track.popularity,
        artists=db_artists
    )


def top_track_to_top_track_db(top_track) -> TopTrackDB:
    return TopTrackDB(
        user_id=top_track.user_id,
        track_id=top_track.track_id,
        collection_date=top_track.collection_date,
        time_range=top_track.time_range,
        position=top_track.position,
        position_change=top_track.position_change,
    )
