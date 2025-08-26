from unittest import mock

import pytest
from sqlalchemy.orm import Session

from src.repositories.profile_repository import ProfileRepository
from src.models.dto import Profile
from src.models.db import ProfileDB


@pytest.fixture
def profile_repo(db_session: Session) -> ProfileRepository:
    return ProfileRepository(db_session)


@pytest.fixture
def mock_profile_db() -> ProfileDB:
    return ProfileDB(
        id="123",
        display_name="Test User",
        email="test@example.com",
        images=[{"height": 300, "url": "http://example.com/image.jpg", "width": 300}],
        spotify_url="https://spotify.com/testuser",
        followers=10,
    )


def test_upsert_inserts_new_profile(
    profile_repo: ProfileRepository, 
    db_session: Session, 
    caplog: pytest.LogCaptureFixture,
    mock_profile_db: ProfileDB,
) -> None:
    with mock.patch("src.repositories.profile_repository.profile_to_profile_db") as mock_profile_to_profile_db:
        mock_profile_to_profile_db.return_value = mock_profile_db

        profile_repo.upsert(
            Profile(id="", display_name="", email=None, images=[], spotify_url="", followers=0)
        )

        db_profile = db_session.get(ProfileDB, "123")
        assert db_profile is not None
        assert db_profile.id == "123"
        assert db_profile.display_name == "Test User"
        assert db_profile.email == "test@example.com"
        assert db_profile.images == [{"height": 300, "url": "http://example.com/image.jpg", "width": 300}]
        assert db_profile.spotify_url == "https://spotify.com/testuser"
        assert db_profile.followers == 10
        assert "Inserting new profile with id: 123" in caplog.text


def test_upsert_updates_existing_profile(
    profile_repo: ProfileRepository, 
    db_session: Session,
    caplog: pytest.LogCaptureFixture,
    mock_profile_db: ProfileDB,
) -> None:
    existing = mock_profile_db
    db_session.add(existing)
    db_session.commit()
    profile = Profile(
        id="123",
        display_name="Updated User",
        email="updated@example.com",
        images=[{"height": 300, "url": "http://example.com/image.jpg", "width": 300}],
        spotify_url="https://spotify.com/updateduser",
        followers=20,
    )

    profile_repo.upsert(profile)

    db_profile = db_session.get(ProfileDB, "123")
    assert db_profile.display_name == "Updated User"
    assert db_profile.email == "updated@example.com"
    assert db_profile.spotify_url == "https://spotify.com/updateduser"
    assert db_profile.followers == 20
    assert "Updating existing profile with id: 123" in caplog.text
