import pytest
from datetime import date
from unittest.mock import Mock

from src.models.enums import TimeRange
from src.models.domain import Artist
from src.pipelines.top_genres_pipeline import TopGenresPipeline


def test_single_artist_single_genre():
    """Test with one artist having one genre"""
    artists = [
        Artist(
            id="artist1",
            name="Test Artist",
            images=[],
            spotify_url="https://spotify.com/artist1",
            genres=["rock"],
            followers=1000,
            popularity=50,
        )
    ]

    result = TopGenresPipeline._get_top_genres(
        artists=artists,
        user_id="user123",
        time_range=TimeRange.SHORT_TERM,
        collection_date=date(2024, 1, 1),
    )

    assert len(result) == 1
    assert result[0].genre_id == "rock"
    assert result[0].percentage == 1.0
    assert result[0].position == 1
    assert result[0].user_id == "user123"
    assert result[0].time_range == TimeRange.SHORT_TERM


def test_multiple_artists_same_genre():
    """Test with multiple artists having the same genre"""
    artists = [
        Artist(
            id="artist1",
            name="Artist 1",
            images=[],
            spotify_url="",
            genres=["rock"],
            followers=0,
            popularity=0,
        ),
        Artist(
            id="artist2",
            name="Artist 2",
            images=[],
            spotify_url="",
            genres=["rock"],
            followers=0,
            popularity=0,
        ),
        Artist(
            id="artist3",
            name="Artist 3",
            images=[],
            spotify_url="",
            genres=["rock"],
            followers=0,
            popularity=0,
        ),
    ]

    result = TopGenresPipeline._get_top_genres(
        artists=artists,
        user_id="user123",
        time_range=TimeRange.MEDIUM_TERM,
        collection_date=date(2024, 1, 1),
    )

    assert len(result) == 1
    assert result[0].genre_id == "rock"
    assert result[0].percentage == 1.0
    assert result[0].position == 1


def test_multiple_genres_different_frequencies():
    """Test with multiple genres having different frequencies"""
    artists = [
        Artist(
            id="artist1",
            name="Artist 1",
            images=[],
            spotify_url="",
            genres=["rock"],
            followers=0,
            popularity=0,
        ),
        Artist(
            id="artist2",
            name="Artist 2",
            images=[],
            spotify_url="",
            genres=["rock"],
            followers=0,
            popularity=0,
        ),
        Artist(
            id="artist3",
            name="Artist 3",
            images=[],
            spotify_url="",
            genres=["pop"],
            followers=0,
            popularity=0,
        ),
        Artist(
            id="artist4",
            name="Artist 4",
            images=[],
            spotify_url="",
            genres=["jazz"],
            followers=0,
            popularity=0,
        ),
    ]

    result = TopGenresPipeline._get_top_genres(
        artists=artists,
        user_id="user123",
        time_range=TimeRange.LONG_TERM,
        collection_date=date(2024, 1, 1),
    )

    assert len(result) == 3
    # Should be sorted by frequency (rock=2, pop=1, jazz=1)
    assert result[0].genre_id == "rock"
    assert result[0].percentage == 0.5  # 2/4
    assert result[0].position == 1

    # pop and jazz should be tied for second place
    assert result[1].genre_id in ["pop", "jazz"]
    assert result[1].percentage == 0.25  # 1/4
    assert result[1].position == 2

    assert result[2].genre_id in ["pop", "jazz"]
    assert result[2].percentage == 0.25  # 1/4
    assert result[2].position == 3


def test_artist_with_multiple_genres():
    """Test with artists having multiple genres each"""
    artists = [
        Artist(
            id="artist1",
            name="Artist 1",
            images=[],
            spotify_url="",
            genres=["rock", "metal"],
            followers=0,
            popularity=0,
        ),
        Artist(
            id="artist2",
            name="Artist 2",
            images=[],
            spotify_url="",
            genres=["pop", "dance"],
            followers=0,
            popularity=0,
        ),
        Artist(
            id="artist3",
            name="Artist 3",
            images=[],
            spotify_url="",
            genres=["rock", "pop"],
            followers=0,
            popularity=0,
        ),
    ]

    result = TopGenresPipeline._get_top_genres(
        artists=artists,
        user_id="user123",
        time_range=TimeRange.SHORT_TERM,
        collection_date=date(2024, 1, 1),
    )

    assert len(result) == 4  # rock, metal, pop, dance

    # Count frequencies: rock=2, pop=2, metal=1, dance=1
    genre_counts = {item.genre_id: item.percentage for item in result}

    # rock and pop should be tied for first
    assert genre_counts["rock"] == 0.33  # 2/6, rounded to 2 decimal places
    assert genre_counts["pop"] == 0.33  # 2/6, rounded to 2 decimal places
    assert genre_counts["metal"] == 0.17  # 1/6, rounded to 2 decimal places
    assert genre_counts["dance"] == 0.17  # 1/6, rounded to 2 decimal places


def test_more_than_five_genres():
    """Test that only top 5 genres are returned"""
    artists = [
        Artist(
            id=f"artist{i}",
            name=f"Artist {i}",
            images=[],
            spotify_url="",
            genres=[f"genre{i}"],
            followers=0,
            popularity=0,
        )
        for i in range(10)  # 10 different genres
    ]

    result = TopGenresPipeline._get_top_genres(
        artists=artists,
        user_id="user123",
        time_range=TimeRange.SHORT_TERM,
        collection_date=date(2024, 1, 1),
    )

    assert len(result) == 5  # Should only return top 5
    assert all(item.position == i + 1 for i, item in enumerate(result))


def test_empty_artists_list():
    """Test with empty artists list"""
    result = TopGenresPipeline._get_top_genres(
        artists=[],
        user_id="user123",
        time_range=TimeRange.SHORT_TERM,
        collection_date=date(2024, 1, 1),
    )

    assert len(result) == 0


def test_artists_with_no_genres():
    """Test with artists that have empty genre lists"""
    artists = [
        Artist(
            id="artist1",
            name="Artist 1",
            images=[],
            spotify_url="",
            genres=[],
            followers=0,
            popularity=0,
        ),
        Artist(
            id="artist2",
            name="Artist 2",
            images=[],
            spotify_url="",
            genres=[],
            followers=0,
            popularity=0,
        ),
    ]

    result = TopGenresPipeline._get_top_genres(
        artists=artists,
        user_id="user123",
        time_range=TimeRange.SHORT_TERM,
        collection_date=date(2024, 1, 1),
    )

    assert len(result) == 0


def test_percentage_calculation_accuracy():
    """Test that percentages are calculated and rounded correctly"""
    artists = [
        Artist(
            id="artist1",
            name="Artist 1",
            images=[],
            spotify_url="",
            genres=["genre1"],
            followers=0,
            popularity=0,
        ),
        Artist(
            id="artist2",
            name="Artist 2",
            images=[],
            spotify_url="",
            genres=["genre1"],
            followers=0,
            popularity=0,
        ),
        Artist(
            id="artist3",
            name="Artist 3",
            images=[],
            spotify_url="",
            genres=["genre2"],
            followers=0,
            popularity=0,
        ),
    ]

    result = TopGenresPipeline._get_top_genres(
        artists=artists,
        user_id="user123",
        time_range=TimeRange.SHORT_TERM,
        collection_date=date(2024, 1, 1),
    )

    assert len(result) == 2
    # genre1: 2/3 = 0.666... -> 0.67
    # genre2: 1/3 = 0.333... -> 0.33
    assert result[0].percentage == 0.67
    assert result[1].percentage == 0.33


def test_position_assignment():
    """Test that positions are assigned correctly (1-based indexing)"""
    artists = [
        Artist(
            id="artist1",
            name="Artist 1",
            images=[],
            spotify_url="",
            genres=["genre1"],
            followers=0,
            popularity=0,
        ),
        Artist(
            id="artist2",
            name="Artist 2",
            images=[],
            spotify_url="",
            genres=["genre2"],
            followers=0,
            popularity=0,
        ),
        Artist(
            id="artist3",
            name="Artist 3",
            images=[],
            spotify_url="",
            genres=["genre3"],
            followers=0,
            popularity=0,
        ),
    ]

    result = TopGenresPipeline._get_top_genres(
        artists=artists,
        user_id="user123",
        time_range=TimeRange.SHORT_TERM,
        collection_date=date(2024, 1, 1),
    )

    assert len(result) == 3
    assert result[0].position == 1
    assert result[1].position == 2
    assert result[2].position == 3


def test_tied_genres_ordering():
    """Test that tied genres maintain consistent ordering"""
    artists = [
        Artist(
            id="artist1",
            name="Artist 1",
            images=[],
            spotify_url="",
            genres=["genre_a"],
            followers=0,
            popularity=0,
        ),
        Artist(
            id="artist2",
            name="Artist 2",
            images=[],
            spotify_url="",
            genres=["genre_b"],
            followers=0,
            popularity=0,
        ),
    ]

    result = TopGenresPipeline._get_top_genres(
        artists=artists,
        user_id="user123",
        time_range=TimeRange.SHORT_TERM,
        collection_date=date(2024, 1, 1),
    )

    assert len(result) == 2
    # Both should have 50% and positions 1 and 2
    # The exact order may depend on Counter.most_common() implementation
    assert all(item.percentage == 0.5 for item in result)
    assert set(item.position for item in result) == {1, 2}
