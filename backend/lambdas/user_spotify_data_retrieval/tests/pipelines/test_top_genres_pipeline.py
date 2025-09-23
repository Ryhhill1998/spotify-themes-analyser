import datetime
import pytest
from sqlalchemy.orm import Session

from src.repositories.top_items.top_genres_repository import TopGenresRepository
from src.models.db import ProfileDB
from src.models.enums import TimeRange
from src.pipelines.top_genres_pipeline import TopGenresPipeline


@pytest.fixture
def top_genres_pipeline(db_session: Session) -> TopGenresPipeline:
    top_genres_repository = TopGenresRepository(db_session=db_session)

    return TopGenresPipeline(top_genres_repository=top_genres_repository)


@pytest.mark.asyncio
async def test_top_genres_pipeline_run_adds_top_genres_to_db(
    db_session: Session,
    top_genres_pipeline: TopGenresPipeline,
    existing_profile: ProfileDB,
) -> None:
    access_token = "access_token"
    user_id = existing_profile.id
    time_range = TimeRange.SHORT_TERM
    collection_date = datetime.date.today()

    genres = await top_genres_pipeline.run()
