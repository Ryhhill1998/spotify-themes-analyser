from typing import AsyncGenerator
import httpx
import pytest

import pytest_asyncio
from sqlalchemy.orm import Session

from src.models.db import ProfileDB
from src.models.shared import Image
from src.models.domain import Profile
from src.repositories.profile_repository import ProfileRepository
from src.services.spotify_service import SpotifyService
from src.pipelines.profile_pipeline import ProfilePipeline

PROFILE_DATA = {
    "country": "X",
    "display_name": "First",
    "email": "first.last@domain.com",
    "explicit_content": {"filter_enabled": False, "filter_locked": False},
    "external_urls": {"spotify": "https://open.spotify.com/user/123"},
    "followers": {"href": None, "total": 16},
    "href": "https://api.spotify.com/v1/users/123",
    "id": "123",
    "images": [
        {"url": "https://i.scdn.co/image/456", "height": 300, "width": 300},
        {"url": "https://i.scdn.co/image/789", "height": 64, "width": 64},
    ],
    "product": "premium",
    "type": "user",
    "uri": "spotify:user:123",
}


@pytest_asyncio.fixture
async def spotify_service(httpx_mock) -> AsyncGenerator[SpotifyService, None]:
    httpx_mock.add_response(
        method="GET",
        url="http://localhost:8000/me",
        json=PROFILE_DATA,
        status_code=200,
    )

    async with httpx.AsyncClient() as client:
        yield SpotifyService(client=client, base_url="http://localhost:8000")


@pytest.fixture
def profile_pipeline(
    db_session: Session, spotify_service: SpotifyService
) -> ProfilePipeline:
    profile_repository = ProfileRepository(db_session)

    return ProfilePipeline(
        spotify_service=spotify_service, profile_repository=profile_repository
    )


@pytest.mark.asyncio
async def test_profile_pipeline_run_returns_expected_profile(
    profile_pipeline: ProfilePipeline,
) -> None:
    access_token = "access_token"

    profile = await profile_pipeline.run(access_token)

    expected_profile = Profile(
        id="123",
        display_name="First",
        email="first.last@domain.com",
        images=[
            Image(url="https://i.scdn.co/image/456", height=300, width=300),
            Image(url="https://i.scdn.co/image/789", height=64, width=64),
        ],
        spotify_url="https://open.spotify.com/user/123",
        followers=16,
    )
    assert profile == expected_profile


@pytest.mark.asyncio
async def test_profile_pipeline_run_adds_profile_to_db(
    profile_pipeline: ProfilePipeline,
    db_session: Session,
) -> None:
    access_token = "access_token"

    await profile_pipeline.run(access_token)

    profile = db_session.get(ProfileDB, "123")
    assert (
        profile.display_name == "First"
        and profile.email == "first.last@domain.com"
        and profile.images
        == [
            {"url": "https://i.scdn.co/image/456", "height": 300, "width": 300},
            {"url": "https://i.scdn.co/image/789", "height": 64, "width": 64},
        ]
        and profile.spotify_url == "https://open.spotify.com/user/123"
        and profile.followers == 16
    )


@pytest.mark.asyncio
async def test_profile_pipeline_run_updates_profile_in_db_if_already_exists(
    profile_pipeline: ProfilePipeline, db_session: Session, existing_profile: ProfileDB
) -> None:
    creation_timestamp = db_session.get(
        ProfileDB, existing_profile.id
    ).creation_timestamp
    access_token = "access_token"

    await profile_pipeline.run(access_token)

    db_session.commit()
    profile = db_session.get(ProfileDB, "123")
    assert (
        profile.display_name == "First"
        and profile.email == "first.last@domain.com"
        and profile.images
        == [
            {"url": "https://i.scdn.co/image/456", "height": 300, "width": 300},
            {"url": "https://i.scdn.co/image/789", "height": 64, "width": 64},
        ]
        and profile.spotify_url == "https://open.spotify.com/user/123"
        and profile.followers == 16
        and profile.creation_timestamp == creation_timestamp
    )
