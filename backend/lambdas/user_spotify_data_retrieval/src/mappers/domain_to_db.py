from src.models.db import ArtistDB, ProfileDB, TopArtistDB
from src.models.domain import SpotifyArtist, SpotifyProfile, TopArtist


def spotify_profile_to_profile_db(spotify_profile: SpotifyProfile) -> ProfileDB:
    return ProfileDB(
        id=spotify_profile.id,
        display_name=spotify_profile.display_name,
        email=spotify_profile.email,
        images=[image.model_dump() for image in spotify_profile.images],
        spotify_url=spotify_profile.spotify_url,
        followers=spotify_profile.followers,
    )


def spotify_artist_to_artist_db(spotify_artist: SpotifyArtist) -> ArtistDB:
    return ArtistDB(
        id=spotify_artist.id,
        name=spotify_artist.name,
        images=[image.model_dump() for image in spotify_artist.images],
        spotify_url=spotify_artist.spotify_url,
        genres=spotify_artist.genres,
        followers=spotify_artist.followers,
        popularity=spotify_artist.popularity,
    )


def top_artist_to_top_artist_db(top_artist: TopArtist) -> TopArtistDB:
    return TopArtistDB(
        user_id=top_artist.id,
        artist_id=top_artist.artist_id,
        collection_date=top_artist.collection_date,
        time_range=top_artist.time_range,
        position=top_artist.position,
        position_change=top_artist.position_change,
    )
