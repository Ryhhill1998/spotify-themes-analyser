from src.components.users.models.domain import SpotifyUser, User
from src.shared.spotify.data_service import SpotifyDataService
from httpx import AsyncClient


class SpotifyUserService(SpotifyDataService):
    def __init__(self, client: AsyncClient, base_url: str):
        super().__init__(client=client, base_url=base_url)

    async def get_user(self, access_token: str) -> User:
        data = await self._get_data(endpoint="me", access_token=access_token)
        spotify_user = SpotifyUser(**data)
        user = User.from_spotify_user(spotify_user)

        return user