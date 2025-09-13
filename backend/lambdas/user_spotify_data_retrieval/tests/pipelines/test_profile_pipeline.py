import pytest

from sqlalchemy.orm import Session

from src.repositories.profile_repository import ProfileRepository
from src.services.spotify_service import SpotifyService
from src.pipelines.profile_pipeline import ProfilePipeline


@pytest.fixture
def profile_pipeline(
    db_session: Session, spotify_service: SpotifyService
) -> ProfilePipeline:
    profile_repository = ProfileRepository(db_session)

    return ProfilePipeline(
        spotify_service=spotify_service, profile_repository=profile_repository
    )


@pytest.mark.asyncio
async def test_profile_pipeline_run(profile_pipeline: ProfilePipeline) -> None:
    access_token = "access_token"

    profile = await profile_pipeline.run(access_token)

    print(profile)
