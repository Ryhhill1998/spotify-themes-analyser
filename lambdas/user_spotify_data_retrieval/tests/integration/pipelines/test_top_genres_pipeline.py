import datetime
import pytest
from sqlalchemy.orm import Session

from src.models.domain import Artist, TopGenre
from src.models.shared import Image
from src.repositories.top_items.top_genres_repository import TopGenresRepository
from src.models.db import ProfileDB, TopGenreDB
from src.models.enums import TimeRange
from src.pipelines.top_genres_pipeline import TopGenresPipeline

ARTISTS = [
    Artist(
        id="2n2RSaZqBuUUukhbLlpnE6",
        name="Sleep Token",
        images=[
            Image(
                height=640,
                url="https://i.scdn.co/image/ab6761610000e5ebd00c2ff422829437e6b5f1e0",
                width=640,
            ),
            Image(
                height=320,
                url="https://i.scdn.co/image/ab67616100005174d00c2ff422829437e6b5f1e0",
                width=320,
            ),
            Image(
                height=160,
                url="https://i.scdn.co/image/ab6761610000f178d00c2ff422829437e6b5f1e0",
                width=160,
            ),
        ],
        spotify_url="https://open.spotify.com/artist/2n2RSaZqBuUUukhbLlpnE6",
        genres=["progressive metal", "metalcore"],
        followers=2689316,
        popularity=82,
    ),
    Artist(
        id="6NnBBumbcMYsaPTHFhPtXD",
        name="VOILÀ",
        images=[
            Image(
                height=640,
                url="https://i.scdn.co/image/ab6761610000e5eb2b8c0a420a952a14a2e23c9c",
                width=640,
            ),
            Image(
                height=320,
                url="https://i.scdn.co/image/ab676161000051742b8c0a420a952a14a2e23c9c",
                width=320,
            ),
            Image(
                height=160,
                url="https://i.scdn.co/image/ab6761610000f1782b8c0a420a952a14a2e23c9c",
                width=160,
            ),
        ],
        spotify_url="https://open.spotify.com/artist/6NnBBumbcMYsaPTHFhPtXD",
        genres=[],
        followers=327844,
        popularity=70,
    ),
    Artist(
        id="6TIYQ3jFPwQSRmorSezPxX",
        name="mgk",
        images=[
            Image(
                height=640,
                url="https://i.scdn.co/image/ab6761610000e5eb85e7615a199f8b17fabfcd61",
                width=640,
            ),
            Image(
                height=320,
                url="https://i.scdn.co/image/ab6761610000517485e7615a199f8b17fabfcd61",
                width=320,
            ),
            Image(
                height=160,
                url="https://i.scdn.co/image/ab6761610000f17885e7615a199f8b17fabfcd61",
                width=160,
            ),
        ],
        spotify_url="https://open.spotify.com/artist/6TIYQ3jFPwQSRmorSezPxX",
        genres=[],
        followers=5615062,
        popularity=82,
    ),
    Artist(
        id="70BYFdaZbEKbeauJ670ysI",
        name="Shinedown",
        images=[
            Image(
                height=640,
                url="https://i.scdn.co/image/ab6761610000e5eb5c83ee58ebb4cfeed8a528e2",
                width=640,
            ),
            Image(
                height=320,
                url="https://i.scdn.co/image/ab676161000051745c83ee58ebb4cfeed8a528e2",
                width=320,
            ),
            Image(
                height=160,
                url="https://i.scdn.co/image/ab6761610000f1785c83ee58ebb4cfeed8a528e2",
                width=160,
            ),
        ],
        spotify_url="https://open.spotify.com/artist/70BYFdaZbEKbeauJ670ysI",
        genres=["post-grunge", "alternative metal", "rock"],
        followers=4499344,
        popularity=75,
    ),
    Artist(
        id="4oUHIQIBe0LHzYfvXNW4QM",
        name="Morgan Wallen",
        images=[
            Image(
                height=640,
                url="https://i.scdn.co/image/ab6761610000e5eb4245b1652fcc23f2b76ccd07",
                width=640,
            ),
            Image(
                height=320,
                url="https://i.scdn.co/image/ab676161000051744245b1652fcc23f2b76ccd07",
                width=320,
            ),
            Image(
                height=160,
                url="https://i.scdn.co/image/ab6761610000f1784245b1652fcc23f2b76ccd07",
                width=160,
            ),
        ],
        spotify_url="https://open.spotify.com/artist/4oUHIQIBe0LHzYfvXNW4QM",
        genres=["country"],
        followers=13629163,
        popularity=94,
    ),
    Artist(
        id="6Ad91Jof8Niiw0lGLLi3NW",
        name="YUNGBLUD",
        images=[
            Image(
                height=640,
                url="https://i.scdn.co/image/ab6761610000e5eb7c9287712c4355e54c94e0d0",
                width=640,
            ),
            Image(
                height=320,
                url="https://i.scdn.co/image/ab676161000051747c9287712c4355e54c94e0d0",
                width=320,
            ),
            Image(
                height=160,
                url="https://i.scdn.co/image/ab6761610000f1787c9287712c4355e54c94e0d0",
                width=160,
            ),
        ],
        spotify_url="https://open.spotify.com/artist/6Ad91Jof8Niiw0lGLLi3NW",
        genres=[],
        followers=3068496,
        popularity=77,
    ),
    Artist(
        id="6XyY86QOPPrYVGvF9ch6wz",
        name="Linkin Park",
        images=[
            Image(
                height=640,
                url="https://i.scdn.co/image/ab6761610000e5eb527d95dabbe8b8b527e8136f",
                width=640,
            ),
            Image(
                height=320,
                url="https://i.scdn.co/image/ab67616100005174527d95dabbe8b8b527e8136f",
                width=320,
            ),
            Image(
                height=160,
                url="https://i.scdn.co/image/ab6761610000f178527d95dabbe8b8b527e8136f",
                width=160,
            ),
        ],
        spotify_url="https://open.spotify.com/artist/6XyY86QOPPrYVGvF9ch6wz",
        genres=["nu metal", "rap metal", "rock", "alternative metal"],
        followers=31236950,
        popularity=92,
    ),
    Artist(
        id="39VNwvlQTqE9SvgPjjnMpc",
        name="NOTHING MORE",
        images=[
            Image(
                height=640,
                url="https://i.scdn.co/image/ab6761610000e5ebcd7961c989876a2982feb13e",
                width=640,
            ),
            Image(
                height=320,
                url="https://i.scdn.co/image/ab67616100005174cd7961c989876a2982feb13e",
                width=320,
            ),
            Image(
                height=160,
                url="https://i.scdn.co/image/ab6761610000f178cd7961c989876a2982feb13e",
                width=160,
            ),
        ],
        spotify_url="https://open.spotify.com/artist/39VNwvlQTqE9SvgPjjnMpc",
        genres=[],
        followers=572590,
        popularity=68,
    ),
    Artist(
        id="3Ngh2zDBRPEriyxQDAMKd1",
        name="Matchbox Twenty",
        images=[
            Image(
                height=640,
                url="https://i.scdn.co/image/ab6761610000e5eb2600695faee2deeb736755f0",
                width=640,
            ),
            Image(
                height=320,
                url="https://i.scdn.co/image/ab676161000051742600695faee2deeb736755f0",
                width=320,
            ),
            Image(
                height=160,
                url="https://i.scdn.co/image/ab6761610000f1782600695faee2deeb736755f0",
                width=160,
            ),
        ],
        spotify_url="https://open.spotify.com/artist/3Ngh2zDBRPEriyxQDAMKd1",
        genres=["post-grunge"],
        followers=2672282,
        popularity=71,
    ),
    Artist(
        id="3T55D3LMiygE9eSKFpiAye",
        name="Badflower",
        images=[
            Image(
                height=640,
                url="https://i.scdn.co/image/ab6761610000e5ebd1634326a43dfa2aea839053",
                width=640,
            ),
            Image(
                height=320,
                url="https://i.scdn.co/image/ab67616100005174d1634326a43dfa2aea839053",
                width=320,
            ),
            Image(
                height=160,
                url="https://i.scdn.co/image/ab6761610000f178d1634326a43dfa2aea839053",
                width=160,
            ),
        ],
        spotify_url="https://open.spotify.com/artist/3T55D3LMiygE9eSKFpiAye",
        genres=["post-grunge"],
        followers=355499,
        popularity=57,
    ),
]


@pytest.fixture
def top_genres_pipeline(db_session: Session) -> TopGenresPipeline:
    top_genres_repository = TopGenresRepository(db_session=db_session)

    return TopGenresPipeline(top_genres_repository=top_genres_repository)


@pytest.mark.integration
def test_top_genres_pipeline_run_adds_top_genres_to_db(
    db_session: Session,
    top_genres_pipeline: TopGenresPipeline,
    existing_profile: ProfileDB,
) -> None:
    user_id = existing_profile.id
    time_range = TimeRange.SHORT_TERM
    collection_date = datetime.date.today()

    top_genres_pipeline.run(
        artists=ARTISTS,
        user_id=user_id,
        time_range=time_range,
        collection_date=collection_date,
    )

    top_genres = [
        TopGenre(
            user_id=genre.user_id,
            genre_id=genre.genre_id,
            collection_date=genre.collection_date,
            time_range=genre.time_range,
            position=genre.position,
            percentage=genre.percentage,
        )
        for genre in db_session.query(TopGenreDB).all()
    ]
    expected_top_genres = [
        TopGenre(
            user_id=user_id,
            genre_id="post-grunge",
            collection_date=collection_date,
            time_range=time_range,
            position=1,
            percentage=0.33,
        ),
        TopGenre(
            user_id=user_id,
            genre_id="alternative metal",
            collection_date=collection_date,
            time_range=time_range,
            position=2,
            percentage=0.22,
        ),
        TopGenre(
            user_id=user_id,
            genre_id="rock",
            collection_date=collection_date,
            time_range=time_range,
            position=3,
            percentage=0.22,
        ),
        TopGenre(
            user_id=user_id,
            genre_id="progressive metal",
            collection_date=collection_date,
            time_range=time_range,
            position=4,
            percentage=0.11,
        ),
        TopGenre(
            user_id=user_id,
            genre_id="metalcore",
            collection_date=collection_date,
            time_range=time_range,
            position=5,
            percentage=0.11,
        ),
    ]
    assert top_genres == expected_top_genres
