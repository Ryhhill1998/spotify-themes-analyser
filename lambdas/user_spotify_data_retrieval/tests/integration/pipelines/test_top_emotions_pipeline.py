import asyncio
import datetime
from typing import AsyncGenerator
import httpx
import pytest
import pytest_asyncio
from sqlalchemy.orm import Session

from src.models.domain import (
    Track,
    TrackArtist,
    TrackLyrics,
    TrackEmotionalProfile,
    EmotionalProfile,
    TopEmotion,
)
from src.models.enums import TimeRange, PositionChange
from src.models.db import (
    ProfileDB,
    TopEmotionDB,
    TrackLyricsDB,
    TrackEmotionalProfileDB,
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
    TrackEmotionalProfile(
        track_id="track1",
        emotional_profile=EmotionalProfile(
            joy=0.8,
            sadness=0.1,
            anger=0.0,
            fear=0.0,
            love=0.7,
            hope=0.6,
            nostalgia=0.2,
            loneliness=0.1,
            confidence=0.5,
            despair=0.0,
            excitement=0.4,
            mystery=0.1,
            defiance=0.2,
            gratitude=0.3,
            spirituality=0.1,
        ),
    ),
    TrackEmotionalProfile(
        track_id="track2",
        emotional_profile=EmotionalProfile(
            joy=0.1,
            sadness=0.9,
            anger=0.2,
            fear=0.1,
            love=0.3,
            hope=0.1,
            nostalgia=0.8,
            loneliness=0.7,
            confidence=0.2,
            despair=0.6,
            excitement=0.0,
            mystery=0.3,
            defiance=0.1,
            gratitude=0.1,
            spirituality=0.2,
        ),
    ),
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
def emotional_profiles_service(db_session: Session) -> EmotionalProfilesService:
    emotional_profile_repository = TrackEmotionalProfilesRepository(db_session)

    # Create a mock model service that returns predictable results
    class MockModelService:
        async def get_emotional_profile(self, lyrics: str) -> EmotionalProfile:
            if "happy" in lyrics.lower():
                return EmotionalProfile(
                    joy=0.8,
                    sadness=0.1,
                    anger=0.0,
                    fear=0.0,
                    love=0.7,
                    hope=0.6,
                    nostalgia=0.2,
                    loneliness=0.1,
                    confidence=0.5,
                    despair=0.0,
                    excitement=0.4,
                    mystery=0.1,
                    defiance=0.2,
                    gratitude=0.3,
                    spirituality=0.1,
                )
            else:  # sad lyrics
                return EmotionalProfile(
                    joy=0.1,
                    sadness=0.9,
                    anger=0.2,
                    fear=0.1,
                    love=0.3,
                    hope=0.1,
                    nostalgia=0.8,
                    loneliness=0.7,
                    confidence=0.2,
                    despair=0.6,
                    excitement=0.0,
                    mystery=0.3,
                    defiance=0.1,
                    gratitude=0.1,
                    spirituality=0.2,
                )

    mock_model_service = MockModelService()
    return EmotionalProfilesService(
        emotional_profile_repository=emotional_profile_repository,
        model_service=mock_model_service,
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
async def test_top_emotions_pipeline_run_stores_top_emotions_in_db(
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

    top_emotions_in_db = db_session.query(TopEmotionDB).all()
    assert len(top_emotions_in_db) > 0
    assert all(emotion.user_id == user_id for emotion in top_emotions_in_db)
    assert all(emotion.time_range == time_range for emotion in top_emotions_in_db)
    assert all(
        emotion.collection_date == collection_date for emotion in top_emotions_in_db
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_top_emotions_pipeline_run_adds_top_emotions_to_db(
    top_emotions_pipeline: TopEmotionsPipeline,
    db_session: Session,
    test_tracks_in_db: list[TrackDB],
) -> None:
    user_id = "test_user"
    time_range = TimeRange.SHORT_TERM
    collection_date = datetime.date(2024, 1, 15)

    await top_emotions_pipeline.run(
        tracks=TEST_TRACKS,
        user_id=user_id,
        time_range=time_range,
        collection_date=collection_date,
    )

    # Verify top emotions were stored
    top_emotions_in_db = db_session.query(TopEmotionDB).all()
    assert len(top_emotions_in_db) > 0

    # Check that emotions are ranked by percentage (highest first)
    percentages = [emotion.percentage for emotion in top_emotions_in_db]
    assert percentages == sorted(percentages, reverse=True)

    # Verify all emotions have the correct user_id and time_range
    for emotion in top_emotions_in_db:
        assert emotion.user_id == user_id
        assert emotion.time_range == time_range
        assert emotion.collection_date == collection_date

    # Verify positions are sequential starting from 1
    positions = [emotion.position for emotion in top_emotions_in_db]
    assert positions == list(range(1, len(positions) + 1))


@pytest.mark.integration
@pytest.mark.asyncio
async def test_top_emotions_pipeline_run_handles_position_changes(
    top_emotions_pipeline: TopEmotionsPipeline,
    db_session: Session,
    test_tracks_in_db: list[TrackDB],
) -> None:
    user_id = "test_user"
    time_range = TimeRange.SHORT_TERM
    collection_date = datetime.date(2024, 1, 15)

    # First run - create initial top emotions
    await top_emotions_pipeline.run(
        tracks=TEST_TRACKS,
        user_id=user_id,
        time_range=time_range,
        collection_date=collection_date,
    )

    # Get the first run results
    first_run_emotions = db_session.query(TopEmotionDB).all()
    assert len(first_run_emotions) > 0

    # Second run with different tracks to create position changes
    # First create the additional track in the database
    track3 = TrackDB(
        id="track3",
        name="New Song",
        images=[],
        spotify_url="https://open.spotify.com/track/track3",
        album_name="New Album",
        release_date="2024-01-03",
        explicit=False,
        duration_ms=190000,
        popularity=90,
    )

    db_session.add(track3)
    db_session.commit()

    different_tracks = [
        Track(
            id="track3",
            name="New Song",
            images=[],
            spotify_url="https://open.spotify.com/track/track3",
            album_name="New Album",
            release_date="2024-01-03",
            explicit=False,
            duration_ms=190000,
            popularity=90,
            artists=[TrackArtist(id="artist3", name="New Artist")],
        ),
    ]

    await top_emotions_pipeline.run(
        tracks=different_tracks,
        user_id=user_id,
        time_range=time_range,
        collection_date=collection_date,
    )

    # Verify position changes were calculated
    top_emotions_in_db = db_session.query(TopEmotionDB).all()
    position_changes = [emotion.position_change for emotion in top_emotions_in_db]

    # Should have some position changes (new entries, moved entries, etc.)
    assert any(change is not None for change in position_changes)

    # Verify we have more emotions now (from both runs)
    assert len(top_emotions_in_db) > len(first_run_emotions)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_top_emotions_pipeline_run_handles_empty_tracks_list(
    top_emotions_pipeline: TopEmotionsPipeline,
    db_session: Session,
    test_tracks_in_db: list[TrackDB],
) -> None:
    user_id = "test_user"
    time_range = TimeRange.SHORT_TERM
    collection_date = datetime.date(2024, 1, 15)

    # Run with empty tracks list
    await top_emotions_pipeline.run(
        tracks=[],
        user_id=user_id,
        time_range=time_range,
        collection_date=collection_date,
    )

    # Should not crash and should not create any top emotions
    top_emotions_in_db = db_session.query(TopEmotionDB).all()
    assert len(top_emotions_in_db) == 0

    # Should not create any lyrics or emotional profiles either
    lyrics_in_db = db_session.query(TrackLyricsDB).all()
    assert len(lyrics_in_db) == 0

    profiles_in_db = db_session.query(TrackEmotionalProfileDB).all()
    assert len(profiles_in_db) == 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_top_emotions_pipeline_run_aggregates_emotions_correctly(
    top_emotions_pipeline: TopEmotionsPipeline,
    db_session: Session,
    test_tracks_in_db: list[TrackDB],
) -> None:
    user_id = "test_user"
    time_range = TimeRange.SHORT_TERM
    collection_date = datetime.date(2024, 1, 15)

    await top_emotions_pipeline.run(
        tracks=TEST_TRACKS,
        user_id=user_id,
        time_range=time_range,
        collection_date=collection_date,
    )

    # Verify that emotions are properly aggregated and normalized
    top_emotions_in_db = db_session.query(TopEmotionDB).all()

    # Should have multiple emotions
    assert len(top_emotions_in_db) > 0

    # All percentages should be between 0 and 1 (normalized)
    for emotion in top_emotions_in_db:
        assert 0 <= emotion.percentage <= 1

    # Should have emotions from both tracks (joy should be high due to happy song)
    emotion_ids = [emotion.emotion_id for emotion in top_emotions_in_db]
    assert "joy" in emotion_ids
    assert "sadness" in emotion_ids

    # Verify that percentages sum to approximately 1.0 (normalized)
    total_percentage = sum(emotion.percentage for emotion in top_emotions_in_db)
    assert abs(total_percentage - 1.0) < 0.01  # Allow for small rounding errors
