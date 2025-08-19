from src.components.profile.models.domain import Profile
from src.components.profile.data import SpotifyProfileService
from src.components.profile.repository import ProfileRepository


class ProfileOrchestrator:
    def __init__(self, data: SpotifyProfileService, repository: ProfileRepository):
        self.data = data
        self.repository = repository

    async def get_and_store_user_profile(self, access_token: str) -> Profile:
        profile = await self.data.get_profile(access_token=access_token)
        self.repository.store_user_profile(profile=profile)
        return profile
