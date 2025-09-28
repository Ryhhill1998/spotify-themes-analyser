import pytest
from datetime import date
from unittest.mock import Mock
from collections import defaultdict

from src.models.enums import TimeRange
from src.models.domain import TrackEmotionalProfile, EmotionalProfile
from src.pipelines.top_emotions_pipeline import TopEmotionsPipeline


def test_single_emotional_profile():
    """Test aggregation with a single emotional profile"""
    emotional_profile = EmotionalProfile(
        joy=0.3,
        sadness=0.4,
        anger=0.2,
        excitement=0.1,
        fear=0.0,
        love=0.0,
        hope=0.0,
        nostalgia=0.0,
        loneliness=0.0,
        confidence=0.0,
        despair=0.0,
        mystery=0.0,
        defiance=0.0,
        gratitude=0.0,
        spirituality=0.0,
    )
    profile_response = TrackEmotionalProfile(
        track_id="track1", emotional_profile=emotional_profile
    )

    result = TopEmotionsPipeline._aggregate_emotions([profile_response])

    assert result["joy"] == 0.3
    assert result["sadness"] == 0.4
    assert result["anger"] == 0.2
    assert result["excitement"] == 0.1


def test_multiple_emotional_profiles_same_emotions():
    """Test aggregation with multiple profiles having the same emotions"""
    profiles = [
        TrackEmotionalProfile(
            track_id="track1",
            emotional_profile=EmotionalProfile(
                joy=0.2,
                sadness=0.3,
                anger=0.5,
                fear=0.0,
                love=0.0,
                hope=0.0,
                nostalgia=0.0,
                loneliness=0.0,
                confidence=0.0,
                despair=0.0,
                excitement=0.0,
                mystery=0.0,
                defiance=0.0,
                gratitude=0.0,
                spirituality=0.0,
            ),
        ),
        TrackEmotionalProfile(
            track_id="track2",
            emotional_profile=EmotionalProfile(
                joy=0.4,
                sadness=0.1,
                anger=0.5,
                fear=0.0,
                love=0.0,
                hope=0.0,
                nostalgia=0.0,
                loneliness=0.0,
                confidence=0.0,
                despair=0.0,
                excitement=0.0,
                mystery=0.0,
                defiance=0.0,
                gratitude=0.0,
                spirituality=0.0,
            ),
        ),
        TrackEmotionalProfile(
            track_id="track3",
            emotional_profile=EmotionalProfile(
                joy=0.0,
                sadness=0.2,
                anger=0.8,
                fear=0.0,
                love=0.0,
                hope=0.0,
                nostalgia=0.0,
                loneliness=0.0,
                confidence=0.0,
                despair=0.0,
                excitement=0.0,
                mystery=0.0,
                defiance=0.0,
                gratitude=0.0,
                spirituality=0.0,
            ),
        ),
    ]

    result = TopEmotionsPipeline._aggregate_emotions(profiles)

    # Averages: joy=(0.2+0.4+0.0)/3=0.2, sadness=(0.3+0.1+0.2)/3=0.2, anger=(0.5+0.5+0.8)/3=0.6
    assert result["joy"] == pytest.approx(0.2, rel=1e-10)
    assert result["sadness"] == pytest.approx(0.2, rel=1e-10)
    assert result["anger"] == pytest.approx(0.6, rel=1e-10)


def test_different_emotions_across_profiles():
    """Test aggregation when different profiles have different emotions"""
    profiles = [
        TrackEmotionalProfile(
            track_id="track1",
            emotional_profile=EmotionalProfile(
                joy=0.5,
                sadness=0.3,
                excitement=0.2,
                anger=0.0,
                fear=0.0,
                love=0.0,
                hope=0.0,
                nostalgia=0.0,
                loneliness=0.0,
                confidence=0.0,
                despair=0.0,
                mystery=0.0,
                defiance=0.0,
                gratitude=0.0,
                spirituality=0.0,
            ),
        ),
        TrackEmotionalProfile(
            track_id="track2",
            emotional_profile=EmotionalProfile(
                anger=0.4,
                confidence=0.6,
                joy=0.0,
                sadness=0.0,
                fear=0.0,
                love=0.0,
                hope=0.0,
                nostalgia=0.0,
                loneliness=0.0,
                despair=0.0,
                excitement=0.0,
                mystery=0.0,
                defiance=0.0,
                gratitude=0.0,
                spirituality=0.0,
            ),
        ),
        TrackEmotionalProfile(
            track_id="track3",
            emotional_profile=EmotionalProfile(
                joy=0.1,
                excitement=0.9,
                sadness=0.0,
                anger=0.0,
                fear=0.0,
                love=0.0,
                hope=0.0,
                nostalgia=0.0,
                loneliness=0.0,
                confidence=0.0,
                despair=0.0,
                mystery=0.0,
                defiance=0.0,
                gratitude=0.0,
                spirituality=0.0,
            ),
        ),
    ]

    result = TopEmotionsPipeline._aggregate_emotions(profiles)

    # joy: (0.5 + 0.1) / 2 = 0.3
    # sadness: 0.3 / 1 = 0.3
    # excitement: (0.2 + 0.9) / 2 = 0.55
    # anger: 0.4 / 1 = 0.4
    # confidence: 0.6 / 1 = 0.6
    assert result["joy"] == pytest.approx(0.3, rel=1e-10)
    assert result["sadness"] == pytest.approx(0.3, rel=1e-10)
    assert result["excitement"] == pytest.approx(0.55, rel=1e-10)
    assert result["anger"] == pytest.approx(0.4, rel=1e-10)
    assert result["confidence"] == pytest.approx(0.6, rel=1e-10)


def test_empty_profiles_list():
    """Test aggregation with empty profiles list"""
    result = TopEmotionsPipeline._aggregate_emotions([])
    assert result == {}


def test_single_emotion_across_profiles():
    """Test aggregation when all profiles have only one emotion"""
    profiles = [
        TrackEmotionalProfile(
            track_id="track1",
            emotional_profile=EmotionalProfile(
                joy=0.8,
                sadness=0.0,
                anger=0.0,
                fear=0.0,
                love=0.0,
                hope=0.0,
                nostalgia=0.0,
                loneliness=0.0,
                confidence=0.0,
                despair=0.0,
                excitement=0.0,
                mystery=0.0,
                defiance=0.0,
                gratitude=0.0,
                spirituality=0.0,
            ),
        ),
        TrackEmotionalProfile(
            track_id="track2",
            emotional_profile=EmotionalProfile(
                joy=0.2,
                sadness=0.0,
                anger=0.0,
                fear=0.0,
                love=0.0,
                hope=0.0,
                nostalgia=0.0,
                loneliness=0.0,
                confidence=0.0,
                despair=0.0,
                excitement=0.0,
                mystery=0.0,
                defiance=0.0,
                gratitude=0.0,
                spirituality=0.0,
            ),
        ),
    ]

    result = TopEmotionsPipeline._aggregate_emotions(profiles)

    assert len(result) == 1
    assert result["joy"] == pytest.approx(0.5, rel=1e-10)


def test_zero_values_included():
    """Test that zero values are included in aggregation"""
    profiles = [
        TrackEmotionalProfile(
            track_id="track1",
            emotional_profile=EmotionalProfile(
                joy=0.0,
                sadness=0.5,
                anger=0.5,
                fear=0.0,
                love=0.0,
                hope=0.0,
                nostalgia=0.0,
                loneliness=0.0,
                confidence=0.0,
                despair=0.0,
                excitement=0.0,
                mystery=0.0,
                defiance=0.0,
                gratitude=0.0,
                spirituality=0.0,
            ),
        ),
        TrackEmotionalProfile(
            track_id="track2",
            emotional_profile=EmotionalProfile(
                joy=0.0,
                sadness=0.3,
                anger=0.7,
                fear=0.0,
                love=0.0,
                hope=0.0,
                nostalgia=0.0,
                loneliness=0.0,
                confidence=0.0,
                despair=0.0,
                excitement=0.0,
                mystery=0.0,
                defiance=0.0,
                gratitude=0.0,
                spirituality=0.0,
            ),
        ),
    ]

    result = TopEmotionsPipeline._aggregate_emotions(profiles)

    assert result["joy"] == 0.0
    assert result["sadness"] == pytest.approx(0.4, rel=1e-10)
    assert result["anger"] == pytest.approx(0.6, rel=1e-10)


def test_basic_ranking_and_normalization():
    """Test basic ranking and normalization functionality"""
    average_emotions = {"joy": 0.3, "sadness": 0.5, "anger": 0.2}

    result = TopEmotionsPipeline._rank_and_normalise_emotions(average_emotions, n=3)

    # Should be ranked by value: sadness > joy > anger
    # Normalized: sadness=0.5/1.0=0.5, joy=0.3/1.0=0.3, anger=0.2/1.0=0.2
    assert len(result) == 3
    assert result["sadness"] == 0.5
    assert result["joy"] == 0.3
    assert result["anger"] == 0.2


def test_n_parameter_limits_results():
    """Test that n parameter limits the number of results"""
    average_emotions = {
        "emotion1": 0.1,
        "emotion2": 0.2,
        "emotion3": 0.3,
        "emotion4": 0.4,
        "emotion5": 0.5,
    }

    result = TopEmotionsPipeline._rank_and_normalise_emotions(average_emotions, n=3)

    assert len(result) == 3
    # Should contain the top 3 emotions
    assert "emotion5" in result
    assert "emotion4" in result
    assert "emotion3" in result
    assert "emotion1" not in result
    assert "emotion2" not in result


def test_n_larger_than_available_emotions():
    """Test when n is larger than available emotions"""
    average_emotions = {"emotion1": 0.3, "emotion2": 0.7}

    result = TopEmotionsPipeline._rank_and_normalise_emotions(average_emotions, n=5)

    assert len(result) == 2
    assert "emotion1" in result
    assert "emotion2" in result


def test_tied_emotions():
    """Test handling of tied emotion values"""
    average_emotions = {"emotion1": 0.3, "emotion2": 0.3, "emotion3": 0.4}

    result = TopEmotionsPipeline._rank_and_normalise_emotions(average_emotions, n=3)

    assert len(result) == 3
    # All should be included, normalization should work correctly
    total = sum(result.values())
    assert total == pytest.approx(1.0, rel=1e-10)


def test_single_emotion():
    """Test with single emotion"""
    average_emotions = {"joy": 0.8}

    result = TopEmotionsPipeline._rank_and_normalise_emotions(average_emotions, n=5)

    assert len(result) == 1
    assert result["joy"] == 1.0  # Should be normalized to 1.0


def test_empty_emotions_dict():
    """Test with empty emotions dictionary"""
    result = TopEmotionsPipeline._rank_and_normalise_emotions({}, n=5)
    assert result == {}


def test_rounding_to_two_decimal_places():
    """Test that results are rounded to 2 decimal places"""
    average_emotions = {"emotion1": 1.0, "emotion2": 2.0, "emotion3": 3.0}

    result = TopEmotionsPipeline._rank_and_normalise_emotions(average_emotions, n=3)

    # Total = 6.0, so normalized values should be 1/6, 2/6, 3/6
    # 1/6 = 0.1666... -> 0.17
    # 2/6 = 0.3333... -> 0.33
    # 3/6 = 0.5 -> 0.5
    assert result["emotion3"] == 0.5
    assert result["emotion2"] == 0.33
    assert result["emotion1"] == 0.17


def test_normalization_preserves_ranking():
    """Test that normalization preserves the original ranking order"""
    average_emotions = {"low": 0.1, "medium": 0.5, "high": 0.9}

    result = TopEmotionsPipeline._rank_and_normalise_emotions(average_emotions, n=3)

    # Should maintain the same order: high > medium > low
    emotions = list(result.keys())
    assert emotions[0] == "high"
    assert emotions[1] == "medium"
    assert emotions[2] == "low"


def test_complete_emotion_processing_pipeline():
    """Test the complete emotion processing pipeline"""
    emotional_profiles = [
        TrackEmotionalProfile(
            track_id="track1",
            emotional_profile=EmotionalProfile(
                joy=0.3,
                sadness=0.4,
                anger=0.3,
                fear=0.0,
                love=0.0,
                hope=0.0,
                nostalgia=0.0,
                loneliness=0.0,
                confidence=0.0,
                despair=0.0,
                excitement=0.0,
                mystery=0.0,
                defiance=0.0,
                gratitude=0.0,
                spirituality=0.0,
            ),
        ),
        TrackEmotionalProfile(
            track_id="track2",
            emotional_profile=EmotionalProfile(
                joy=0.5,
                sadness=0.2,
                excitement=0.3,
                anger=0.0,
                fear=0.0,
                love=0.0,
                hope=0.0,
                nostalgia=0.0,
                loneliness=0.0,
                confidence=0.0,
                despair=0.0,
                mystery=0.0,
                defiance=0.0,
                gratitude=0.0,
                spirituality=0.0,
            ),
        ),
        TrackEmotionalProfile(
            track_id="track3",
            emotional_profile=EmotionalProfile(
                sadness=0.6,
                anger=0.4,
                joy=0.0,
                fear=0.0,
                love=0.0,
                hope=0.0,
                nostalgia=0.0,
                loneliness=0.0,
                confidence=0.0,
                despair=0.0,
                excitement=0.0,
                mystery=0.0,
                defiance=0.0,
                gratitude=0.0,
                spirituality=0.0,
            ),
        ),
    ]

    result = TopEmotionsPipeline._get_top_emotions(
        emotional_profiles=emotional_profiles,
        user_id="user123",
        time_range=TimeRange.SHORT_TERM,
        collection_date=date(2024, 1, 1),
        n=3,
    )

    assert len(result) == 3
    assert all(item.user_id == "user123" for item in result)
    assert all(item.time_range == TimeRange.SHORT_TERM for item in result)
    assert all(item.collection_date == date(2024, 1, 1) for item in result)
    assert all(item.position == i + 1 for i, item in enumerate(result))

    # Check that percentages sum to 1.0 (within rounding error)
    total_percentage = sum(item.percentage for item in result)
    assert total_percentage == pytest.approx(1.0, rel=1e-2)


def test_default_n_parameter():
    """Test that default n=5 is used when not specified"""
    emotional_profiles = [
        TrackEmotionalProfile(
            track_id="track1",
            emotional_profile=EmotionalProfile(
                joy=0.5,
                sadness=0.5,
                anger=0.0,
                fear=0.0,
                love=0.0,
                hope=0.0,
                nostalgia=0.0,
                loneliness=0.0,
                confidence=0.0,
                despair=0.0,
                excitement=0.0,
                mystery=0.0,
                defiance=0.0,
                gratitude=0.0,
                spirituality=0.0,
            ),
        )
    ]

    result = TopEmotionsPipeline._get_top_emotions(
        emotional_profiles=emotional_profiles,
        user_id="user123",
        time_range=TimeRange.MEDIUM_TERM,
        collection_date=date(2024, 1, 1),
    )

    assert len(result) == 2  # Only 2 emotions available
    assert all(item.position == i + 1 for i, item in enumerate(result))


def test_empty_emotional_profiles():
    """Test with empty emotional profiles list"""
    result = TopEmotionsPipeline._get_top_emotions(
        emotional_profiles=[],
        user_id="user123",
        time_range=TimeRange.LONG_TERM,
        collection_date=date(2024, 1, 1),
    )

    assert len(result) == 0


def test_single_emotional_profile():
    """Test with single emotional profile"""
    emotional_profiles = [
        TrackEmotionalProfile(
            track_id="track1",
            emotional_profile=EmotionalProfile(
                joy=0.6,
                sadness=0.4,
                anger=0.0,
                fear=0.0,
                love=0.0,
                hope=0.0,
                nostalgia=0.0,
                loneliness=0.0,
                confidence=0.0,
                despair=0.0,
                excitement=0.0,
                mystery=0.0,
                defiance=0.0,
                gratitude=0.0,
                spirituality=0.0,
            ),
        )
    ]

    result = TopEmotionsPipeline._get_top_emotions(
        emotional_profiles=emotional_profiles,
        user_id="user123",
        time_range=TimeRange.SHORT_TERM,
        collection_date=date(2024, 1, 1),
    )

    assert len(result) == 2
    assert result[0].emotion_id == "joy"
    assert result[0].percentage == 0.6
    assert result[0].position == 1
    assert result[1].emotion_id == "sadness"
    assert result[1].percentage == 0.4
    assert result[1].position == 2


def test_position_assignment():
    """Test that positions are assigned correctly (1-based indexing)"""
    emotional_profiles = [
        TrackEmotionalProfile(
            track_id="track1",
            emotional_profile=EmotionalProfile(
                joy=0.1,
                sadness=0.2,
                anger=0.3,
                fear=0.0,
                love=0.0,
                hope=0.0,
                nostalgia=0.0,
                loneliness=0.0,
                confidence=0.0,
                despair=0.0,
                excitement=0.0,
                mystery=0.0,
                defiance=0.0,
                gratitude=0.0,
                spirituality=0.0,
            ),
        )
    ]

    result = TopEmotionsPipeline._get_top_emotions(
        emotional_profiles=emotional_profiles,
        user_id="user123",
        time_range=TimeRange.SHORT_TERM,
        collection_date=date(2024, 1, 1),
        n=3,
    )

    assert len(result) == 3
    assert result[0].position == 1
    assert result[1].position == 2
    assert result[2].position == 3
