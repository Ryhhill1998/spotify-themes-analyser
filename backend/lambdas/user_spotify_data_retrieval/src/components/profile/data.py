from src.components.profile.models.domain import SpotifyProfile, Profile
from src.shared.spotify.data_service import SpotifyDataService
from httpx import AsyncClient


class SpotifyProfileService(SpotifyDataService):
    def __init__(self, client: AsyncClient, base_url: str):
        super().__init__(client=client, base_url=base_url)

    async def get_profile(self, access_token: str) -> Profile:
        data = await self._get_data(endpoint="me", access_token=access_token)
        spotify_profile = SpotifyProfile(**data)
        profile = Profile.from_spotify_profile(spotify_profile)

        return profile