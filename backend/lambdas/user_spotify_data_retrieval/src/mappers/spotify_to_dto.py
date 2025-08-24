from src.models.dto import Profile, Artist, Track
from src.models.spotify import SpotifyProfile, SpotifyArtist, SpotifyTrack


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


def spotify_artist_to_artist(spotify_artist: SpotifyArtist) -> Artist:
    return Artist(
        id=spotify_artist.id,
        name=spotify_artist.name,
        images=[img.model_dump() for img in spotify_artist.images],
        spotify_url=spotify_artist.external_urls.spotify,
        genres=spotify_artist.genres,
        followers=spotify_artist.followers.total,
        popularity=spotify_artist.popularity,
    )
