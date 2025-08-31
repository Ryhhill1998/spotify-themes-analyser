from datetime import date
from httpx import AsyncClient
import asyncio
from src.repositories.top_items.top_tracks_repository import TopTracksRepository
from src.repositories.tracks_repository import TracksRepository
from src.models.enums import TimeRange
from src.repositories.artists_repository import ArtistsRepository
from src.repositories.top_items.top_artists_repository import TopArtistsRepository
from src.core.db import get_db_session
from src.repositories.profile_repository import ProfileRepository
from src.services.spotify_service import SpotifyService
from src.pipelines.profile_pipeline import ProfilePipeline
from src.pipelines.top_artists_pipeline import TopArtistsPipeline
from src.pipelines.top_tracks_pipeline import TopTracksPipeline

access_token = "BQAklHa4Kq2tMq-llB7h3frYdzaxh48J7ObdjwYXPRByR6nbGHxnv-xPzSqZp_Zq-OO6tcQNUKfa5BTvhenalZzKxHS3cBbucVDki29BzLGQukZhBh0sbLpbyY8jce3rQw8zXb2PdUh6UzZWsFCvtXc614ykdfPqh_A7Ro7sozgcJIGc760ZPItPctUbket2qbngQzohi9wOjCZ8ThtAdUGV1j7ABR1GoRfTN7wfLDj2jil_PpmbtCzs"


async def main():
    client = AsyncClient()
    spotify_service = SpotifyService(client=client, base_url="https://api.spotify.com/v1")

    with get_db_session() as db_session:
        profile_repository = ProfileRepository(db_session)
        profile_pipeline = ProfilePipeline(spotify_service=spotify_service, profile_repository=profile_repository)
        profile = await profile_pipeline.run(access_token)
        print(profile)
        print()

        collection_date = date.today()

        artists_repository = ArtistsRepository(db_session)
        top_artists_repository = TopArtistsRepository(db_session)
        top_artists_pipeline = TopArtistsPipeline(
            spotify_service=spotify_service, artists_repository=artists_repository, top_artists_repository=top_artists_repository
        )
        top_artists = await top_artists_pipeline.run(
            access_token=access_token, user_id=profile.id, time_range=TimeRange.SHORT_TERM, collection_date=collection_date
        )
        print(top_artists)

        tracks_repository = TracksRepository(db_session)
        top_tracks_repository = TopTracksRepository(db_session)
        top_tracks_pipeline = TopTracksPipeline(
            spotify_service=spotify_service, 
            artists_repository=artists_repository, 
            tracks_repository=tracks_repository,
            top_tracks_repository=top_tracks_repository,
        )
        top_tracks = await top_tracks_pipeline.run(
            access_token=access_token, user_id=profile.id, time_range=TimeRange.SHORT_TERM, collection_date=collection_date
        )
        print(top_tracks)


def handler(event, context):
    asyncio.run(main())
    

handler("", "")
