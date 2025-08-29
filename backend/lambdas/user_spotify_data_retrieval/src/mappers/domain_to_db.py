from src.models.db import ArtistDB, ProfileDB
from src.models.domain import SpotifyArtist, SpotifyProfile


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
