import pytest
from sqlalchemy.orm import Session

from src.repositories.profile_repository import ProfileRepository
from src.models.dto import Profile
from src.models.db import ProfileDB


@pytest.fixture
def profile_repo(db_session: Session) -> ProfileRepository:
    return ProfileRepository(db_session)


def test_upsert_creates_new_profile_if_it_does_not_exist(
        profile_repo: ProfileRepository, db_session: Session
) -> None:
    profile = Profile(
        id="user123",
        display_name="Test User",
        email="test email",
        images=[{"height": 300, "url": "http://image.url", "width": 300}],
        spotify_url="http://spotify.url",
        followers=100,
    )
