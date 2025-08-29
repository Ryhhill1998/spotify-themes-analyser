from src.models.db import ProfileDB
from src.models.domain import SpotifyProfile


def spotify_profile_to_profile_db(spotify_profile: SpotifyProfile) -> ProfileDB:
    return ProfileDB(
        id=spotify_profile.id,
        display_name=spotify_profile.display_name,
        email=spotify_profile.email,
        images=[image.model_dump() for image in spotify_profile.images],
        spotify_url=spotify_profile.spotify_url,
        followers=spotify_profile.followers,
    )
