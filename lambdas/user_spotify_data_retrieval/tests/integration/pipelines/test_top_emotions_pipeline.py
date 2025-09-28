import asyncio
import datetime
from typing import AsyncGenerator
import httpx
import pytest
import pytest_asyncio
from sqlalchemy.orm import Session

from src.services.emotional_profiles.model_service import (
    EmotionalProfileCalculator,
)
from src.models.domain import (
    TopEmotion,
    Track,
    TrackArtist,
    TrackLyrics,
    EmotionalProfile,
)
from src.models.enums import TimeRange, PositionChange
from src.models.db import (
    ProfileDB,
    TopEmotionDB,
    TrackDB,
)
from src.repositories.track_lyrics_repository import TrackLyricsRepository
from src.repositories.track_emotional_profiles_repository import (
    TrackEmotionalProfilesRepository,
)
from src.repositories.top_items.top_emotions_repository import TopEmotionsRepository
from src.services.lyrics.lyrics_service import LyricsService
from src.services.lyrics.lyrics_scraper import LyricsScraper
from src.services.emotional_profiles.emotional_profiles_service import (
    EmotionalProfilesService,
)
from src.pipelines.top_emotions_pipeline import TopEmotionsPipeline

# Test data
TEST_TRACKS = [
    Track(
        id="track1",
        name="Happy Song",
        images=[],
        spotify_url="https://open.spotify.com/track/track1",
        album_name="Happy Album",
        release_date="2024-01-01",
        explicit=False,
        duration_ms=180000,
        popularity=80,
        artists=[TrackArtist(id="artist1", name="Happy Artist")],
    ),
    Track(
        id="track2",
        name="Sad Song",
        images=[],
        spotify_url="https://open.spotify.com/track/track2",
        album_name="Sad Album",
        release_date="2024-01-02",
        explicit=False,
        duration_ms=200000,
        popularity=70,
        artists=[TrackArtist(id="artist2", name="Sad Artist")],
    ),
]

TEST_LYRICS = [
    TrackLyrics(
        track_id="track1",
        lyrics="This is a happy song with joyful lyrics and positive vibes!",
    ),
    TrackLyrics(
        track_id="track2",
        lyrics="This is a sad song with melancholy lyrics and tears.",
    ),
]

TEST_EMOTIONAL_PROFILES = [
    EmotionalProfile(
        joy=0.3,
        sadness=0.05,
        anger=0.0,
        fear=0.0,
        love=0.25,
        hope=0.2,
        nostalgia=0.1,
        loneliness=0.05,
        confidence=0.15,
        despair=0.0,
        excitement=0.1,
        mystery=0.05,
        defiance=0.05,
        gratitude=0.1,
        spirituality=0.05,
    ),
    EmotionalProfile(
        joy=0.025,
        sadness=0.45,
        anger=0.1,
        fear=0.05,
        love=0.15,
        hope=0.05,
        nostalgia=0.35,
        loneliness=0.3,
        confidence=0.1,
        despair=0.25,
        excitement=0.0,
        mystery=0.15,
        defiance=0.05,
        gratitude=0.05,
        spirituality=0.1,
    ),
]

# Expected top emotions based on averaging the two test emotional profiles
EXPECTED_TOP_EMOTIONS = [
    {"emotion_id": "sadness", "percentage": 0.25},
    {"emotion_id": "nostalgia", "percentage": 0.22},
    {"emotion_id": "love", "percentage": 0.20},
    {"emotion_id": "loneliness", "percentage": 0.17},
    {"emotion_id": "joy", "percentage": 0.16},
]


@pytest.fixture
def db_tracks(db_session: Session) -> list[TrackDB]:
    """Create test tracks in the database for foreign key constraints"""
    # Create tracks
    track1 = TrackDB(
        id="track1",
        name="Happy Song",
        images=[],
        spotify_url="https://open.spotify.com/track/track1",
        album_name="Happy Album",
        release_date="2024-01-01",
        explicit=False,
        duration_ms=180000,
        popularity=80,
    )
    track2 = TrackDB(
        id="track2",
        name="Sad Song",
        images=[],
        spotify_url="https://open.spotify.com/track/track2",
        album_name="Sad Album",
        release_date="2024-01-02",
        explicit=False,
        duration_ms=200000,
        popularity=70,
    )

    db_session.add(track1)
    db_session.add(track2)
    db_session.commit()

    return [track1, track2]


@pytest_asyncio.fixture
async def lyrics_service(
    httpx_mock, db_session: Session
) -> AsyncGenerator[LyricsService, None]:
    # Mock Genius API responses - URLs are generated as {base_url}/{artist}-{title}-lyrics
    httpx_mock.add_response(
        method="GET",
        url="https://genius.com/Happy-artist-happy-song-lyrics",
        text="<html><body><div data-lyrics-container='true'>This is a happy song with joyful lyrics and positive vibes!</div></body></html>",
        status_code=200,
    )
    httpx_mock.add_response(
        method="GET",
        url="https://genius.com/Sad-artist-sad-song-lyrics",
        text="<html><body><div data-lyrics-container='true'>This is a sad song with melancholy lyrics and tears.</div></body></html>",
        status_code=200,
    )

    async with httpx.AsyncClient() as client:
        lyrics_repository = TrackLyricsRepository(db_session)
        semaphore = asyncio.Semaphore(5)  # Allow up to 5 concurrent requests
        lyrics_scraper = LyricsScraper(
            client=client,
            base_url="https://genius.com",
            headers={"User-Agent": "test"},
            semaphore=semaphore,
        )
        yield LyricsService(
            lyrics_repository=lyrics_repository,
            lyrics_scraper=lyrics_scraper,
        )


@pytest.fixture
def emotional_profile_calculator() -> EmotionalProfileCalculator:
    class Calculator(EmotionalProfileCalculator):
        async def get_emotional_profile(self, lyrics: str) -> EmotionalProfile:
            if "happy" in lyrics:
                return TEST_EMOTIONAL_PROFILES[0]
            else:
                return TEST_EMOTIONAL_PROFILES[1]

    return Calculator()


@pytest.fixture
def emotional_profiles_service(
    db_session: Session, emotional_profile_calculator: EmotionalProfileCalculator
) -> EmotionalProfilesService:
    emotional_profile_repository = TrackEmotionalProfilesRepository(db_session)

    return EmotionalProfilesService(
        emotional_profile_repository=emotional_profile_repository,
        emotional_profile_calculator=emotional_profile_calculator,
    )


@pytest.fixture
def top_emotions_pipeline(
    db_session: Session,
    lyrics_service: LyricsService,
    emotional_profiles_service: EmotionalProfilesService,
) -> TopEmotionsPipeline:
    top_emotions_repository = TopEmotionsRepository(db_session)
    return TopEmotionsPipeline(
        lyrics_service=lyrics_service,
        emotional_profile_service=emotional_profiles_service,
        top_emotions_repository=top_emotions_repository,
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_top_emotions_pipeline_run_adds_top_emotions_to_db(
    top_emotions_pipeline: TopEmotionsPipeline,
    existing_profile: ProfileDB,
    db_session: Session,
    db_tracks: list[TrackDB],
) -> None:
    user_id = existing_profile.id
    time_range = TimeRange.SHORT_TERM
    collection_date = datetime.date(2024, 1, 15)

    await top_emotions_pipeline.run(
        tracks=TEST_TRACKS,
        user_id=user_id,
        time_range=time_range,
        collection_date=collection_date,
    )

    top_emotions_in_db = [
        TopEmotion(
            user_id=emotion.user_id,
            emotion_id=emotion.emotion_id,
            collection_date=emotion.collection_date,
            time_range=emotion.time_range,
            position=emotion.position,
            percentage=emotion.percentage,
        )
        for emotion in db_session.query(TopEmotionDB).all()
    ]
    expected_top_emotions = [
        TopEmotion(
            user_id=user_id,
            emotion_id=emotion["emotion_id"],
            collection_date=collection_date,
            time_range=time_range,
            position=index + 1,
            percentage=emotion["percentage"],
        )
        for index, emotion in enumerate(EXPECTED_TOP_EMOTIONS)
    ]
    assert top_emotions_in_db == expected_top_emotions


@pytest.mark.integration
@pytest.mark.asyncio
async def test_top_emotions_pipeline_run_adds_top_emotions_to_db_with_expected_position_changes(
    top_emotions_pipeline: TopEmotionsPipeline,
    existing_profile: ProfileDB,
    db_session: Session,
    db_tracks: list[TrackDB],
) -> None:
    user_id = existing_profile.id
    time_range = TimeRange.SHORT_TERM
    collection_date = datetime.date(2024, 1, 15)
    previous_collection_date = collection_date - datetime.timedelta(days=7)

    # Create previous emotional profiles in DB to simulate existing data
    previous_emotions = [
        TopEmotionDB(
            user_id=user_id,
            emotion_id="sadness",
            collection_date=previous_collection_date,
            time_range=time_range,
            position=3,  # Was 3rd, now 1st (UP: 3 -> 1)
            percentage=0.6,
            position_change=None,
        ),
        TopEmotionDB(
            user_id=user_id,
            emotion_id="joy",
            collection_date=previous_collection_date,
            time_range=time_range,
            position=2,  # Was 2nd, now 4th (DOWN: 2 -> 4)
            percentage=0.4,
            position_change=None,
        ),
    ]
    db_session.add_all(previous_emotions)
    db_session.commit()

    await top_emotions_pipeline.run(
        tracks=TEST_TRACKS,
        user_id=user_id,
        time_range=time_range,
        collection_date=collection_date,
    )

    # Build expected results with position changes
    expected_top_emotions = [
        TopEmotion(
            user_id=user_id,
            emotion_id=emotion["emotion_id"],
            collection_date=collection_date,
            time_range=time_range,
            position=index + 1,
            percentage=emotion["percentage"],
            position_change=None,
        )
        for index, emotion in enumerate(EXPECTED_TOP_EMOTIONS)
    ]

    # Apply position changes based on expected results
    for emotion in expected_top_emotions:
        if emotion.emotion_id == "sadness":
            emotion.position_change = PositionChange.UP  # 3 -> 1
        elif emotion.emotion_id == "joy":
            emotion.position_change = PositionChange.DOWN  # 2 -> 4
        else:
            emotion.position_change = PositionChange.NEW

    # Get actual results from DB
    top_emotions_in_db = [
        TopEmotion(
            user_id=emotion.user_id,
            emotion_id=emotion.emotion_id,
            collection_date=emotion.collection_date,
            time_range=emotion.time_range,
            position=emotion.position,
            percentage=emotion.percentage,
            position_change=emotion.position_change,
        )
        for emotion in db_session.query(TopEmotionDB)
        .filter(TopEmotionDB.collection_date == collection_date)
        .order_by(TopEmotionDB.position)
        .all()
    ]

    assert top_emotions_in_db == expected_top_emotions
