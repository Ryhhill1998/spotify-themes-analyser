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
    TrackLyricsDB,
    TrackEmotionalProfileDB,
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


@pytest.mark.integration
@pytest.mark.asyncio
async def test_top_emotions_pipeline_run_stores_lyrics_in_database(
    top_emotions_pipeline: TopEmotionsPipeline,
    existing_profile: ProfileDB,
    db_session: Session,
    db_tracks: list[TrackDB],
) -> None:
    """Test that lyrics are properly stored in the TrackLyricsDB table during pipeline execution."""
    user_id = existing_profile.id
    time_range = TimeRange.SHORT_TERM
    collection_date = datetime.date(2024, 1, 15)

    # Verify no lyrics exist in DB before pipeline run
    lyrics_before = db_session.query(TrackLyricsDB).all()
    assert len(lyrics_before) == 0

    await top_emotions_pipeline.run(
        tracks=TEST_TRACKS,
        user_id=user_id,
        time_range=time_range,
        collection_date=collection_date,
    )

    # Verify lyrics were stored in the database
    lyrics_after = db_session.query(TrackLyricsDB).all()
    assert len(lyrics_after) == 2

    # Verify the correct lyrics were stored
    lyrics_by_track_id = {lyric.track_id: lyric.lyrics for lyric in lyrics_after}

    assert "track1" in lyrics_by_track_id
    assert "track2" in lyrics_by_track_id
    assert (
        lyrics_by_track_id["track1"]
        == "This is a happy song with joyful lyrics and positive vibes!"
    )
    assert (
        lyrics_by_track_id["track2"]
        == "This is a sad song with melancholy lyrics and tears."
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_top_emotions_pipeline_run_stores_emotional_profiles_in_database(
    top_emotions_pipeline: TopEmotionsPipeline,
    existing_profile: ProfileDB,
    db_session: Session,
    db_tracks: list[TrackDB],
) -> None:
    """Test that emotional profiles are properly stored in the TrackEmotionalProfileDB table during pipeline execution."""
    user_id = existing_profile.id
    time_range = TimeRange.SHORT_TERM
    collection_date = datetime.date(2024, 1, 15)

    # Verify no emotional profiles exist in DB before pipeline run
    profiles_before = db_session.query(TrackEmotionalProfileDB).all()
    assert len(profiles_before) == 0

    await top_emotions_pipeline.run(
        tracks=TEST_TRACKS,
        user_id=user_id,
        time_range=time_range,
        collection_date=collection_date,
    )

    # Verify emotional profiles were stored in the database
    profiles_after = db_session.query(TrackEmotionalProfileDB).all()
    assert len(profiles_after) == 2

    # Verify the correct emotional profiles were stored
    profiles_by_track_id = {profile.track_id: profile for profile in profiles_after}

    assert "track1" in profiles_by_track_id
    assert "track2" in profiles_by_track_id

    # Check track1 (happy song) emotional profile
    track1_profile = profiles_by_track_id["track1"]
    assert track1_profile.joy == 0.3
    assert track1_profile.sadness == 0.05
    assert track1_profile.anger == 0.0
    assert track1_profile.fear == 0.0
    assert track1_profile.love == 0.25
    assert track1_profile.hope == 0.2
    assert track1_profile.nostalgia == 0.1
    assert track1_profile.loneliness == 0.05
    assert track1_profile.confidence == 0.15
    assert track1_profile.despair == 0.0
    assert track1_profile.excitement == 0.1
    assert track1_profile.mystery == 0.05
    assert track1_profile.defiance == 0.05
    assert track1_profile.gratitude == 0.1
    assert track1_profile.spirituality == 0.05

    # Check track2 (sad song) emotional profile
    track2_profile = profiles_by_track_id["track2"]
    assert track2_profile.joy == 0.025
    assert track2_profile.sadness == 0.45
    assert track2_profile.anger == 0.1
    assert track2_profile.fear == 0.05
    assert track2_profile.love == 0.15
    assert track2_profile.hope == 0.05
    assert track2_profile.nostalgia == 0.35
    assert track2_profile.loneliness == 0.3
    assert track2_profile.confidence == 0.1
    assert track2_profile.despair == 0.25
    assert track2_profile.excitement == 0.0
    assert track2_profile.mystery == 0.15
    assert track2_profile.defiance == 0.05
    assert track2_profile.gratitude == 0.05
    assert track2_profile.spirituality == 0.1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_top_emotions_pipeline_run_complete_integration_flow(
    top_emotions_pipeline: TopEmotionsPipeline,
    existing_profile: ProfileDB,
    db_session: Session,
    db_tracks: list[TrackDB],
) -> None:
    """Test the complete pipeline flow including all database operations."""
    user_id = existing_profile.id
    time_range = TimeRange.SHORT_TERM
    collection_date = datetime.date(2024, 1, 15)

    # Verify no data exists in any of the relevant tables before pipeline run
    lyrics_before = db_session.query(TrackLyricsDB).count()
    profiles_before = db_session.query(TrackEmotionalProfileDB).count()
    top_emotions_before = db_session.query(TopEmotionDB).count()

    assert lyrics_before == 0
    assert profiles_before == 0
    assert top_emotions_before == 0

    await top_emotions_pipeline.run(
        tracks=TEST_TRACKS,
        user_id=user_id,
        time_range=time_range,
        collection_date=collection_date,
    )

    # Verify all data was stored in the database
    lyrics_after = db_session.query(TrackLyricsDB).count()
    profiles_after = db_session.query(TrackEmotionalProfileDB).count()
    top_emotions_after = db_session.query(TopEmotionDB).count()

    assert lyrics_after == 2
    assert profiles_after == 2
    assert top_emotions_after == 5  # Top 5 emotions

    # Verify the complete data flow by checking that all track IDs are consistent
    lyrics_track_ids = {
        lyric.track_id for lyric in db_session.query(TrackLyricsDB).all()
    }
    profile_track_ids = {
        profile.track_id for profile in db_session.query(TrackEmotionalProfileDB).all()
    }
    expected_track_ids = {"track1", "track2"}

    assert lyrics_track_ids == expected_track_ids
    assert profile_track_ids == expected_track_ids

    # Verify that the top emotions were calculated correctly from the stored emotional profiles
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
