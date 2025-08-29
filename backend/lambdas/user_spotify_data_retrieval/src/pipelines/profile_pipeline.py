from src.mappers.domain_to_db import spotify_profile_to_profile_db
from src.models.domain import SpotifyProfile
from src.services.spotify_service import SpotifyService
from src.repositories.profile_repository import ProfileRepository


class ProfilePipeline:
    def __init__(self, spotify_service: SpotifyService, profile_repo: ProfileRepository):
        self.spotify_service = spotify_service
        self.profile_repo = profile_repo

    async def run(self, access_token: str) -> SpotifyProfile:
        # 1. Get profile data from Spotify API
        spotify_profile = await self.spotify_service.get_user_profile(access_token)

        # 2. Transform to ProfileDB
        db_profile = spotify_profile_to_profile_db(spotify_profile)

        # 3. Store in DB
        self.profile_repo.upsert(db_profile)

        # 4. Return profile so caller can use it
        return spotify_profile
