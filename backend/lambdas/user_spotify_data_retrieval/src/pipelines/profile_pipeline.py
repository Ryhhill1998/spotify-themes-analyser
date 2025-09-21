from src.models.domain import Profile
from src.services.spotify_service import SpotifyService, SpotifyServiceException
from src.repositories.profile_repository import ProfileRepository


class ProfilePipelineException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class ProfilePipeline:
    def __init__(
        self, spotify_service: SpotifyService, profile_repository: ProfileRepository
    ):
        self.spotify_service = spotify_service
        self.profile_repository = profile_repository

    async def run(self, access_token: str) -> Profile:
        try:
            # 1. Get profile data from Spotify API
            profile = await self.spotify_service.get_user_profile(access_token)

            # 2. Store in DB
            self.profile_repository.upsert(profile)

            # 3. Return profile so caller can use it
            return profile
        except SpotifyServiceException as e:
            raise ProfilePipelineException("Profile pipeline failed.") from e
        except Exception as e:
            raise ProfilePipelineException(
                "Unexpected error in profile pipeline."
            ) from e
