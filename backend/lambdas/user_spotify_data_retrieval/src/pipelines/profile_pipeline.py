from src.models.domain import Profile
from src.services.spotify_service import SpotifyService
from src.repositories.profile_repository import ProfileRepository


class ProfilePipeline:
    def __init__(self, spotify_service: SpotifyService, profile_repo: ProfileRepository):
        self.spotify_service = spotify_service
        self.profile_repo = profile_repo

    async def run(self, access_token: str) -> Profile:
        # 1. Get profile data from Spotify API
        profile = await self.spotify_service.get_user_profile(access_token)

        # 2. Store in DB
        self.profile_repo.upsert(profile)

        # 3. Return profile so caller can use it
        return profile
