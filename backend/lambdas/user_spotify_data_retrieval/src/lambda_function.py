from datetime import date
import httpx
import asyncio

from src.core.config import Settings
from src.factories.pipeline_factory import PipelineFactory
from src.models.enums import TimeRange
from src.core.db import get_db_session
from src.services.spotify_service import SpotifyService
from src.pipelines.profile_pipeline import ProfilePipeline
from src.pipelines.top_artists_pipeline import TopArtistsPipeline
from src.pipelines.top_tracks_pipeline import TopTracksPipeline

settings = Settings()


async def run_top_artists_and_genres_pipelines(
    top_artists_pipeline: TopArtistsPipeline,
    access_token: str,
    user_id: str,
    time_range: TimeRange,
    collection_date: date,
) -> None:
    await top_artists_pipeline.run(
        access_token=access_token,
        user_id=user_id,
        time_range=time_range,
        collection_date=collection_date,
    )


async def run_top_tracks_and_emotions_pipelines(
    top_tracks_pipeline: TopTracksPipeline,
    access_token: str,
    user_id: str,
    time_range: TimeRange,
    collection_date: date,
) -> None:
    await top_tracks_pipeline.run(
        access_token=access_token,
        user_id=user_id,
        time_range=time_range,
        collection_date=collection_date,
    )


async def main(access_token: str, time_range: TimeRange, collection_date: date) -> None:
    async with httpx.AsyncClient() as client:
        spotify_service = SpotifyService(client=client, base_url=settings.spotify_base_url)

        with get_db_session(settings.db_connection_string) as db_session:
            pipeline_factory = PipelineFactory(spotify_service=spotify_service, db_session=db_session)
            profile_pipeline: ProfilePipeline = pipeline_factory.create_profile_pipeline()
            top_artists_pipeline: TopArtistsPipeline = pipeline_factory.create_top_artists_pipeline()
            top_tracks_pipeline: TopTracksPipeline = pipeline_factory.create_top_tracks_pipeline()

            profile = await profile_pipeline.run(access_token)

            tasks = [
                run_top_artists_and_genres_pipelines(
                    top_artists_pipeline=top_artists_pipeline,
                    access_token=access_token,
                    user_id=profile.id,
                    time_range=time_range,
                    collection_date=collection_date,
                ),
                run_top_tracks_and_emotions_pipelines(
                    top_tracks_pipeline=top_tracks_pipeline,
                    access_token=access_token,
                    user_id=profile.id,
                    time_range=time_range,
                    collection_date=collection_date,
                ),
            ]

            await asyncio.gather(*tasks)

            print("Completed pipeline runs")


def handler(event, context) -> None:
    access_token = "BQAILLagSoHy-MGO82mT0TETxznDWDGP3yVQJdqpzrBdEOL9Q0ec7MT_Wt8dnJSz9T2sBUos4NLMz1SAntphJJbCthEaYo-_1kcIN_HU-9N3HTjejAIQrMoVe5gbVBxZOL9R-Vns_xaFn-RJKBx9uGF4IuhIH9Tg51M2Z7pkxxYOJqOeJRQCpL_qN8tjAxZLsz5tVxtndE1sWDjVNChruia4kJywaebxTj6Q2mOQzFl4CKVi07ujOdnK"
    time_range = TimeRange.SHORT_TERM
    collection_date = date.today()

    asyncio.run(main(access_token=access_token, time_range=time_range, collection_date=collection_date))
    

handler("", "")
