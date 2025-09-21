import datetime
import re
from typing import AsyncGenerator
import httpx
import pytest

import pytest_asyncio
from sqlalchemy.orm import Session

from src.models.domain import Artist, TopArtist
from src.models.enums import PositionChange, TimeRange
from src.models.db import ArtistDB, ProfileDB, TopArtistDB
from src.repositories.artists_repository import ArtistsRepository
from src.repositories.top_items.top_artists_repository import TopArtistsRepository
from src.services.spotify_service import SpotifyService
from src.pipelines.top_artists_pipeline import TopArtistsPipeline

TOP_ARTISTS_DATA = {
    "items": [
        {
            "external_urls": {
                "spotify": "https://open.spotify.com/artist/2n2RSaZqBuUUukhbLlpnE6"
            },
            "followers": {"href": None, "total": 2689316},
            "genres": ["progressive metal", "metalcore"],
            "href": "https://api.spotify.com/v1/artists/2n2RSaZqBuUUukhbLlpnE6",
            "id": "2n2RSaZqBuUUukhbLlpnE6",
            "images": [
                {
                    "height": 640,
                    "url": "https://i.scdn.co/image/ab6761610000e5ebd00c2ff422829437e6b5f1e0",
                    "width": 640,
                },
                {
                    "height": 320,
                    "url": "https://i.scdn.co/image/ab67616100005174d00c2ff422829437e6b5f1e0",
                    "width": 320,
                },
                {
                    "height": 160,
                    "url": "https://i.scdn.co/image/ab6761610000f178d00c2ff422829437e6b5f1e0",
                    "width": 160,
                },
            ],
            "name": "Sleep Token",
            "popularity": 82,
            "type": "artist",
            "uri": "spotify:artist:2n2RSaZqBuUUukhbLlpnE6",
        },
        {
            "external_urls": {
                "spotify": "https://open.spotify.com/artist/6NnBBumbcMYsaPTHFhPtXD"
            },
            "followers": {"href": None, "total": 327844},
            "genres": [],
            "href": "https://api.spotify.com/v1/artists/6NnBBumbcMYsaPTHFhPtXD",
            "id": "6NnBBumbcMYsaPTHFhPtXD",
            "images": [
                {
                    "height": 640,
                    "url": "https://i.scdn.co/image/ab6761610000e5eb2b8c0a420a952a14a2e23c9c",
                    "width": 640,
                },
                {
                    "height": 320,
                    "url": "https://i.scdn.co/image/ab676161000051742b8c0a420a952a14a2e23c9c",
                    "width": 320,
                },
                {
                    "height": 160,
                    "url": "https://i.scdn.co/image/ab6761610000f1782b8c0a420a952a14a2e23c9c",
                    "width": 160,
                },
            ],
            "name": "VOILÀ",
            "popularity": 70,
            "type": "artist",
            "uri": "spotify:artist:6NnBBumbcMYsaPTHFhPtXD",
        },
        {
            "external_urls": {
                "spotify": "https://open.spotify.com/artist/6TIYQ3jFPwQSRmorSezPxX"
            },
            "followers": {"href": None, "total": 5615062},
            "genres": [],
            "href": "https://api.spotify.com/v1/artists/6TIYQ3jFPwQSRmorSezPxX",
            "id": "6TIYQ3jFPwQSRmorSezPxX",
            "images": [
                {
                    "height": 640,
                    "url": "https://i.scdn.co/image/ab6761610000e5eb85e7615a199f8b17fabfcd61",
                    "width": 640,
                },
                {
                    "height": 320,
                    "url": "https://i.scdn.co/image/ab6761610000517485e7615a199f8b17fabfcd61",
                    "width": 320,
                },
                {
                    "height": 160,
                    "url": "https://i.scdn.co/image/ab6761610000f17885e7615a199f8b17fabfcd61",
                    "width": 160,
                },
            ],
            "name": "mgk",
            "popularity": 82,
            "type": "artist",
            "uri": "spotify:artist:6TIYQ3jFPwQSRmorSezPxX",
        },
        {
            "external_urls": {
                "spotify": "https://open.spotify.com/artist/70BYFdaZbEKbeauJ670ysI"
            },
            "followers": {"href": None, "total": 4499344},
            "genres": ["post-grunge", "alternative metal", "rock"],
            "href": "https://api.spotify.com/v1/artists/70BYFdaZbEKbeauJ670ysI",
            "id": "70BYFdaZbEKbeauJ670ysI",
            "images": [
                {
                    "height": 640,
                    "url": "https://i.scdn.co/image/ab6761610000e5eb5c83ee58ebb4cfeed8a528e2",
                    "width": 640,
                },
                {
                    "height": 320,
                    "url": "https://i.scdn.co/image/ab676161000051745c83ee58ebb4cfeed8a528e2",
                    "width": 320,
                },
                {
                    "height": 160,
                    "url": "https://i.scdn.co/image/ab6761610000f1785c83ee58ebb4cfeed8a528e2",
                    "width": 160,
                },
            ],
            "name": "Shinedown",
            "popularity": 75,
            "type": "artist",
            "uri": "spotify:artist:70BYFdaZbEKbeauJ670ysI",
        },
        {
            "external_urls": {
                "spotify": "https://open.spotify.com/artist/4oUHIQIBe0LHzYfvXNW4QM"
            },
            "followers": {"href": None, "total": 13629163},
            "genres": ["country"],
            "href": "https://api.spotify.com/v1/artists/4oUHIQIBe0LHzYfvXNW4QM",
            "id": "4oUHIQIBe0LHzYfvXNW4QM",
            "images": [
                {
                    "height": 640,
                    "url": "https://i.scdn.co/image/ab6761610000e5eb4245b1652fcc23f2b76ccd07",
                    "width": 640,
                },
                {
                    "height": 320,
                    "url": "https://i.scdn.co/image/ab676161000051744245b1652fcc23f2b76ccd07",
                    "width": 320,
                },
                {
                    "height": 160,
                    "url": "https://i.scdn.co/image/ab6761610000f1784245b1652fcc23f2b76ccd07",
                    "width": 160,
                },
            ],
            "name": "Morgan Wallen",
            "popularity": 94,
            "type": "artist",
            "uri": "spotify:artist:4oUHIQIBe0LHzYfvXNW4QM",
        },
        {
            "external_urls": {
                "spotify": "https://open.spotify.com/artist/6Ad91Jof8Niiw0lGLLi3NW"
            },
            "followers": {"href": None, "total": 3068496},
            "genres": [],
            "href": "https://api.spotify.com/v1/artists/6Ad91Jof8Niiw0lGLLi3NW",
            "id": "6Ad91Jof8Niiw0lGLLi3NW",
            "images": [
                {
                    "height": 640,
                    "url": "https://i.scdn.co/image/ab6761610000e5eb7c9287712c4355e54c94e0d0",
                    "width": 640,
                },
                {
                    "height": 320,
                    "url": "https://i.scdn.co/image/ab676161000051747c9287712c4355e54c94e0d0",
                    "width": 320,
                },
                {
                    "height": 160,
                    "url": "https://i.scdn.co/image/ab6761610000f1787c9287712c4355e54c94e0d0",
                    "width": 160,
                },
            ],
            "name": "YUNGBLUD",
            "popularity": 77,
            "type": "artist",
            "uri": "spotify:artist:6Ad91Jof8Niiw0lGLLi3NW",
        },
        {
            "external_urls": {
                "spotify": "https://open.spotify.com/artist/6XyY86QOPPrYVGvF9ch6wz"
            },
            "followers": {"href": None, "total": 31236950},
            "genres": ["nu metal", "rap metal", "rock", "alternative metal"],
            "href": "https://api.spotify.com/v1/artists/6XyY86QOPPrYVGvF9ch6wz",
            "id": "6XyY86QOPPrYVGvF9ch6wz",
            "images": [
                {
                    "height": 640,
                    "url": "https://i.scdn.co/image/ab6761610000e5eb527d95dabbe8b8b527e8136f",
                    "width": 640,
                },
                {
                    "height": 320,
                    "url": "https://i.scdn.co/image/ab67616100005174527d95dabbe8b8b527e8136f",
                    "width": 320,
                },
                {
                    "height": 160,
                    "url": "https://i.scdn.co/image/ab6761610000f178527d95dabbe8b8b527e8136f",
                    "width": 160,
                },
            ],
            "name": "Linkin Park",
            "popularity": 92,
            "type": "artist",
            "uri": "spotify:artist:6XyY86QOPPrYVGvF9ch6wz",
        },
        {
            "external_urls": {
                "spotify": "https://open.spotify.com/artist/39VNwvlQTqE9SvgPjjnMpc"
            },
            "followers": {"href": None, "total": 572590},
            "genres": [],
            "href": "https://api.spotify.com/v1/artists/39VNwvlQTqE9SvgPjjnMpc",
            "id": "39VNwvlQTqE9SvgPjjnMpc",
            "images": [
                {
                    "height": 640,
                    "url": "https://i.scdn.co/image/ab6761610000e5ebcd7961c989876a2982feb13e",
                    "width": 640,
                },
                {
                    "height": 320,
                    "url": "https://i.scdn.co/image/ab67616100005174cd7961c989876a2982feb13e",
                    "width": 320,
                },
                {
                    "height": 160,
                    "url": "https://i.scdn.co/image/ab6761610000f178cd7961c989876a2982feb13e",
                    "width": 160,
                },
            ],
            "name": "NOTHING MORE",
            "popularity": 68,
            "type": "artist",
            "uri": "spotify:artist:39VNwvlQTqE9SvgPjjnMpc",
        },
        {
            "external_urls": {
                "spotify": "https://open.spotify.com/artist/3Ngh2zDBRPEriyxQDAMKd1"
            },
            "followers": {"href": None, "total": 2672282},
            "genres": ["post-grunge"],
            "href": "https://api.spotify.com/v1/artists/3Ngh2zDBRPEriyxQDAMKd1",
            "id": "3Ngh2zDBRPEriyxQDAMKd1",
            "images": [
                {
                    "height": 640,
                    "url": "https://i.scdn.co/image/ab6761610000e5eb2600695faee2deeb736755f0",
                    "width": 640,
                },
                {
                    "height": 320,
                    "url": "https://i.scdn.co/image/ab676161000051742600695faee2deeb736755f0",
                    "width": 320,
                },
                {
                    "height": 160,
                    "url": "https://i.scdn.co/image/ab6761610000f1782600695faee2deeb736755f0",
                    "width": 160,
                },
            ],
            "name": "Matchbox Twenty",
            "popularity": 71,
            "type": "artist",
            "uri": "spotify:artist:3Ngh2zDBRPEriyxQDAMKd1",
        },
        {
            "external_urls": {
                "spotify": "https://open.spotify.com/artist/3T55D3LMiygE9eSKFpiAye"
            },
            "followers": {"href": None, "total": 355499},
            "genres": ["post-grunge"],
            "href": "https://api.spotify.com/v1/artists/3T55D3LMiygE9eSKFpiAye",
            "id": "3T55D3LMiygE9eSKFpiAye",
            "images": [
                {
                    "height": 640,
                    "url": "https://i.scdn.co/image/ab6761610000e5ebd1634326a43dfa2aea839053",
                    "width": 640,
                },
                {
                    "height": 320,
                    "url": "https://i.scdn.co/image/ab67616100005174d1634326a43dfa2aea839053",
                    "width": 320,
                },
                {
                    "height": 160,
                    "url": "https://i.scdn.co/image/ab6761610000f178d1634326a43dfa2aea839053",
                    "width": 160,
                },
            ],
            "name": "Badflower",
            "popularity": 57,
            "type": "artist",
            "uri": "spotify:artist:3T55D3LMiygE9eSKFpiAye",
        },
    ]
}

EXPECTED_ARTISTS = [
    Artist(
        id="2n2RSaZqBuUUukhbLlpnE6",
        name="Sleep Token",
        images=[
            {
                "height": 640,
                "url": "https://i.scdn.co/image/ab6761610000e5ebd00c2ff422829437e6b5f1e0",
                "width": 640,
            },
            {
                "height": 320,
                "url": "https://i.scdn.co/image/ab67616100005174d00c2ff422829437e6b5f1e0",
                "width": 320,
            },
            {
                "height": 160,
                "url": "https://i.scdn.co/image/ab6761610000f178d00c2ff422829437e6b5f1e0",
                "width": 160,
            },
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
            {
                "height": 640,
                "url": "https://i.scdn.co/image/ab6761610000e5eb2b8c0a420a952a14a2e23c9c",
                "width": 640,
            },
            {
                "height": 320,
                "url": "https://i.scdn.co/image/ab676161000051742b8c0a420a952a14a2e23c9c",
                "width": 320,
            },
            {
                "height": 160,
                "url": "https://i.scdn.co/image/ab6761610000f1782b8c0a420a952a14a2e23c9c",
                "width": 160,
            },
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
            {
                "height": 640,
                "url": "https://i.scdn.co/image/ab6761610000e5eb85e7615a199f8b17fabfcd61",
                "width": 640,
            },
            {
                "height": 320,
                "url": "https://i.scdn.co/image/ab6761610000517485e7615a199f8b17fabfcd61",
                "width": 320,
            },
            {
                "height": 160,
                "url": "https://i.scdn.co/image/ab6761610000f17885e7615a199f8b17fabfcd61",
                "width": 160,
            },
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
            {
                "height": 640,
                "url": "https://i.scdn.co/image/ab6761610000e5eb5c83ee58ebb4cfeed8a528e2",
                "width": 640,
            },
            {
                "height": 320,
                "url": "https://i.scdn.co/image/ab676161000051745c83ee58ebb4cfeed8a528e2",
                "width": 320,
            },
            {
                "height": 160,
                "url": "https://i.scdn.co/image/ab6761610000f1785c83ee58ebb4cfeed8a528e2",
                "width": 160,
            },
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
            {
                "height": 640,
                "url": "https://i.scdn.co/image/ab6761610000e5eb4245b1652fcc23f2b76ccd07",
                "width": 640,
            },
            {
                "height": 320,
                "url": "https://i.scdn.co/image/ab676161000051744245b1652fcc23f2b76ccd07",
                "width": 320,
            },
            {
                "height": 160,
                "url": "https://i.scdn.co/image/ab6761610000f1784245b1652fcc23f2b76ccd07",
                "width": 160,
            },
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
            {
                "height": 640,
                "url": "https://i.scdn.co/image/ab6761610000e5eb7c9287712c4355e54c94e0d0",
                "width": 640,
            },
            {
                "height": 320,
                "url": "https://i.scdn.co/image/ab676161000051747c9287712c4355e54c94e0d0",
                "width": 320,
            },
            {
                "height": 160,
                "url": "https://i.scdn.co/image/ab6761610000f1787c9287712c4355e54c94e0d0",
                "width": 160,
            },
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
            {
                "height": 640,
                "url": "https://i.scdn.co/image/ab6761610000e5eb527d95dabbe8b8b527e8136f",
                "width": 640,
            },
            {
                "height": 320,
                "url": "https://i.scdn.co/image/ab67616100005174527d95dabbe8b8b527e8136f",
                "width": 320,
            },
            {
                "height": 160,
                "url": "https://i.scdn.co/image/ab6761610000f178527d95dabbe8b8b527e8136f",
                "width": 160,
            },
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
            {
                "height": 640,
                "url": "https://i.scdn.co/image/ab6761610000e5ebcd7961c989876a2982feb13e",
                "width": 640,
            },
            {
                "height": 320,
                "url": "https://i.scdn.co/image/ab67616100005174cd7961c989876a2982feb13e",
                "width": 320,
            },
            {
                "height": 160,
                "url": "https://i.scdn.co/image/ab6761610000f178cd7961c989876a2982feb13e",
                "width": 160,
            },
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
            {
                "height": 640,
                "url": "https://i.scdn.co/image/ab6761610000e5eb2600695faee2deeb736755f0",
                "width": 640,
            },
            {
                "height": 320,
                "url": "https://i.scdn.co/image/ab676161000051742600695faee2deeb736755f0",
                "width": 320,
            },
            {
                "height": 160,
                "url": "https://i.scdn.co/image/ab6761610000f1782600695faee2deeb736755f0",
                "width": 160,
            },
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
            {
                "height": 640,
                "url": "https://i.scdn.co/image/ab6761610000e5ebd1634326a43dfa2aea839053",
                "width": 640,
            },
            {
                "height": 320,
                "url": "https://i.scdn.co/image/ab67616100005174d1634326a43dfa2aea839053",
                "width": 320,
            },
            {
                "height": 160,
                "url": "https://i.scdn.co/image/ab6761610000f178d1634326a43dfa2aea839053",
                "width": 160,
            },
        ],
        spotify_url="https://open.spotify.com/artist/3T55D3LMiygE9eSKFpiAye",
        genres=["post-grunge"],
        followers=355499,
        popularity=57,
    ),
]


@pytest_asyncio.fixture
async def spotify_service(httpx_mock) -> AsyncGenerator[SpotifyService, None]:
    url_pattern = re.compile("http://localhost:8000/me/top/artists.*")
    httpx_mock.add_response(
        method="GET",
        url=url_pattern,
        json=TOP_ARTISTS_DATA,
        status_code=200,
    )

    async with httpx.AsyncClient() as client:
        yield SpotifyService(client=client, base_url="http://localhost:8000")


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

    assert artists == EXPECTED_ARTISTS


@pytest.mark.asyncio
async def test_top_artists_pipeline_run_adds_artists_to_db(
    db_session: Session,
    top_artists_pipeline: TopArtistsPipeline,
    existing_profile: ProfileDB,
) -> None:
    access_token = "access_token"
    user_id = existing_profile.id
    time_range = TimeRange.SHORT_TERM
    collection_date = datetime.date.today()

    await top_artists_pipeline.run(
        access_token=access_token,
        user_id=user_id,
        time_range=time_range,
        collection_date=collection_date,
    )

    db_artists = db_session.query(ArtistDB).all()
    db_artist_ids = {artist.id for artist in db_artists}
    expected_artist_ids = {artist.id for artist in EXPECTED_ARTISTS}
    assert db_artist_ids == expected_artist_ids


@pytest.mark.asyncio
async def test_top_artists_pipeline_run_adds_top_artists_to_db(
    db_session: Session,
    top_artists_pipeline: TopArtistsPipeline,
    existing_profile: ProfileDB,
) -> None:
    access_token = "access_token"
    user_id = existing_profile.id
    time_range = TimeRange.SHORT_TERM
    collection_date = datetime.date.today()

    await top_artists_pipeline.run(
        access_token=access_token,
        user_id=user_id,
        time_range=time_range,
        collection_date=collection_date,
    )

    top_artists = [
        TopArtist(
            user_id=artist.user_id,
            artist_id=artist.artist_id,
            collection_date=artist.collection_date,
            time_range=artist.time_range,
            position=artist.position,
            position_change=artist.position_change,
        )
        for artist in db_session.query(TopArtistDB).all()
    ]
    expected_top_artists = [
        TopArtist(
            user_id=existing_profile.id,
            artist_id=artist.id,
            collection_date=collection_date,
            time_range=time_range,
            position=index + 1,
            position_change=None,
        )
        for index, artist in enumerate(EXPECTED_ARTISTS)
    ]
    assert top_artists == expected_top_artists


@pytest.mark.asyncio
async def test_top_artists_pipeline_run_adds_top_artists_to_db_with_expected_position_changes(
    db_session: Session,
    top_artists_pipeline: TopArtistsPipeline,
    existing_profile: ProfileDB,
) -> None:
    access_token = "access_token"
    user_id = existing_profile.id
    time_range = TimeRange.SHORT_TERM
    collection_date = datetime.date.today()
    up_artist_ids = set(
        ["2n2RSaZqBuUUukhbLlpnE6", "6TIYQ3jFPwQSRmorSezPxX"]
    )  # 4->1, 6->3
    down_artist_ids = set(
        ["6NnBBumbcMYsaPTHFhPtXD", "4oUHIQIBe0LHzYfvXNW4QM"]
    )  # 1->2, 2->5
    new_artist_ids = set(["6XyY86QOPPrYVGvF9ch6wz"])  # New artist at 7
    artists_to_add = [*EXPECTED_ARTISTS]
    artists_to_add.pop(6)  # Remove artist 7 to simulate it being a new artist
    db_session.add_all(
        [
            ArtistDB(
                id=artist.id,
                name=artist.name,
                images=[image.model_dump() for image in artist.images],
                spotify_url=artist.spotify_url,
                genres=artist.genres,
                followers=artist.followers,
                popularity=artist.popularity,
            )
            for artist in artists_to_add
        ]
    )
    db_session.commit()
    positions = [4, 1, 6, 4, 2, 6, 8, 9, 10]  # Previous positions of the artists
    # Add previous top artists with different positions
    top_artists_to_add = [
        TopArtistDB(
            user_id=existing_profile.id,
            artist_id=artist.id,
            collection_date=collection_date - datetime.timedelta(days=7),
            time_range=time_range,
            position=positions[index],
            position_change=None,
        )
        for index, artist in enumerate(artists_to_add)
    ]
    db_session.add_all(top_artists_to_add)
    db_session.commit()

    await top_artists_pipeline.run(
        access_token=access_token,
        user_id=user_id,
        time_range=time_range,
        collection_date=collection_date,
    )

    db_session.commit()
    top_artists = [
        TopArtist(
            user_id=artist.user_id,
            artist_id=artist.artist_id,
            collection_date=artist.collection_date,
            time_range=artist.time_range,
            position=artist.position,
            position_change=artist.position_change,
        )
        for artist in db_session.query(TopArtistDB)
        .where(TopArtistDB.collection_date == collection_date)
        .all()
    ]
    expected_top_artists = [
        TopArtist(
            user_id=existing_profile.id,
            artist_id=artist.id,
            collection_date=collection_date,
            time_range=time_range,
            position=index + 1,
            position_change=None,
        )
        for index, artist in enumerate(EXPECTED_ARTISTS)
    ]
    for top_artist in expected_top_artists:
        if top_artist.artist_id in up_artist_ids:
            top_artist.position_change = PositionChange.UP
        elif top_artist.artist_id in down_artist_ids:
            top_artist.position_change = PositionChange.DOWN
        elif top_artist.artist_id in new_artist_ids:
            top_artist.position_change = PositionChange.NEW
    assert top_artists == expected_top_artists
