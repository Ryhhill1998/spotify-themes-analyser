import datetime
import pytest

from sqlalchemy.orm import Session

from src.models.enums import TimeRange
from src.models.db import ProfileDB
from src.repositories.artists_repository import ArtistsRepository
from src.repositories.top_items.top_artists_repository import TopArtistsRepository
from src.services.spotify_service import SpotifyService
from src.pipelines.top_artists_pipeline import TopArtistsPipeline


@pytest.fixture
def top_artists_pipeline(
    db_session: Session, spotify_service: SpotifyService
) -> TopArtistsPipeline:
    artists_repository = ArtistsRepository(db_session)
    top_artists_repository = TopArtistsRepository(db_session)

    return TopArtistsPipeline(
        spotify_service=spotify_service,
        artists_repository=artists_repository,
        top_artists_repository=top_artists_repository,
    )


@pytest.mark.asyncio
async def test_top_artists_pipeline_run_returns_expected_artists(
    top_artists_pipeline: TopArtistsPipeline, existing_profile: ProfileDB
) -> None:
    access_token = "access_token"
    user_id = existing_profile.id
    time_range = TimeRange.SHORT_TERM
    collection_date = datetime.date.today()

    artists = await top_artists_pipeline.run(
        access_token=access_token,
        user_id=user_id,
        time_range=time_range,
        collection_date=collection_date,
    )
