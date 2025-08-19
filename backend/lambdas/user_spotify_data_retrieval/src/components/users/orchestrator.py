from backend.lambdas.user_spotify_data_retrieval.src.components.users.data import SpotifyUserService
from backend.lambdas.user_spotify_data_retrieval.src.components.users.models.domain import User
from backend.lambdas.user_spotify_data_retrieval.src.components.users.repository import UserRepository


class UserOrchestrator:
    def __init__(self, data: SpotifyUserService, repository: UserRepository):
        self.data = data
        self.repository = repository

    async def get_and_store_user(self, access_token: str) -> User:
        user = await self.data.get_user(access_token=access_token)
        self.repository.store_user(user)
        return user
