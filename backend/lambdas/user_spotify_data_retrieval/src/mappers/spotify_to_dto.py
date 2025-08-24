from src.models.dto import Profile
from src.models.spotify import SpotifyProfile


def spotify_profile_to_profile(spotify_profile: SpotifyProfile) -> Profile:
    profile = Profile(
        id=spotify_profile.id,
        display_name=spotify_profile.display_name,
        email=spotify_profile.email,
        images=[img.model_dump() for img in spotify_profile.images],
        spotify_url=spotify_profile.href,
        followers=spotify_profile.followers.total,
    )

    return profile
