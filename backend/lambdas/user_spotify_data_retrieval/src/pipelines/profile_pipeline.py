from src.services.spotify_service import SpotifyService
from src.repositories.profile_repo import ProfileRepository
from src.models.dto import Profile


class ProfilePipeline:
    def __init__(self, spotify_service: SpotifyService, profile_repo: ProfileRepository):
        self.spotify_service = spotify_service
        self.profile_repo = profile_repo

    def run(self, access_token: str) -> Profile:
        # 1. Get profile data from Spotify API
        spotify_profile = self.spotify_service.get_profile(access_token)

        # 2. Convert API model to DTO (your service might already do this)
        profile = Profile(
            id=spotify_profile.id,
            display_name=spotify_profile.display_name,
            email=spotify_profile.email,
            images=[img.model_dump() for img in spotify_profile.images],
            spotify_url=spotify_profile.spotify_url,
            followers=spotify_profile.followers,
        )

        # 3. Persist to DB
        self.profile_repo.upsert(profile)

        # 4. Return DTO so caller can use it
        return profile
