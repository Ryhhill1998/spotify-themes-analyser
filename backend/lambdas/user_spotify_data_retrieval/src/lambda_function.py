from datetime import date
import httpx
import asyncio

from backend.lambdas.user_spotify_data_retrieval.src.pipelines.top_emotions_pipeline import TopEmotionsPipeline
from backend.lambdas.user_spotify_data_retrieval.src.services.emotional_profile_service import EmotionalProfileService
from backend.lambdas.user_spotify_data_retrieval.src.services.lyrics_service import LyricsService
from src.pipelines.top_genres_pipeline import TopGenresPipeline
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
    top_genres_pipeline: TopGenresPipeline,
    access_token: str,
    user_id: str,
    time_range: TimeRange,
    collection_date: date,
) -> None:
    top_artists = await top_artists_pipeline.run(
        access_token=access_token,
        user_id=user_id,
        time_range=time_range,
        collection_date=collection_date,
    )
    top_genres_pipeline.run(
        user_id=user_id, time_range=time_range, collection_date=collection_date, artists=top_artists
    )


async def run_top_tracks_and_emotions_pipelines(
    top_tracks_pipeline: TopTracksPipeline,
    top_emotions_pipeline: TopEmotionsPipeline,
    access_token: str,
    user_id: str,
    time_range: TimeRange,
    collection_date: date,
) -> None:
    top_tracks = await top_tracks_pipeline.run(
        access_token=access_token,
        user_id=user_id,
        time_range=time_range,
        collection_date=collection_date,
    )
    await top_emotions_pipeline.run(
        user_id=user_id, time_range=time_range, collection_date=collection_date, tracks=top_tracks
    )


async def main(access_token: str, time_range: TimeRange, collection_date: date) -> None:
    async with httpx.AsyncClient() as client:
        spotify_service = SpotifyService(client=client, base_url=settings.spotify_base_url)
        lyrics_service = LyricsService(client=client, base_url=settings.lyrics_base_url)
        emotional_profile_service = EmotionalProfileService(
            gcp_project_id=settings.gcp_project_id, gcp_location=settings.gcp_location, model_name=settings.model_name
        )

        with get_db_session(settings.db_connection_string) as db_session:
            pipeline_factory = PipelineFactory(
                spotify_service=spotify_service, 
                db_session=db_session,
                lyrics_service=lyrics_service,
                emotional_profile_service=emotional_profile_service,
            )
            profile_pipeline: ProfilePipeline = pipeline_factory.create_profile_pipeline()
            top_artists_pipeline: TopArtistsPipeline = pipeline_factory.create_top_artists_pipeline()
            top_tracks_pipeline: TopTracksPipeline = pipeline_factory.create_top_tracks_pipeline()
            top_genres_pipeline: TopGenresPipeline = pipeline_factory.create_top_genres_pipeline()
            top_emotions_pipeline: TopEmotionsPipeline = pipeline_factory.create_top_emotions_pipeline()

            profile = await profile_pipeline.run(access_token)

            tasks = [
                run_top_artists_and_genres_pipelines(
                    top_artists_pipeline=top_artists_pipeline,
                    top_genres_pipeline=top_genres_pipeline,
                    access_token=access_token,
                    user_id=profile.id,
                    time_range=time_range,
                    collection_date=collection_date,
                ),
                run_top_tracks_and_emotions_pipelines(
                    top_tracks_pipeline=top_tracks_pipeline,
                    top_emotions_pipeline=top_emotions_pipeline,
                    access_token=access_token,
                    user_id=profile.id,
                    time_range=time_range,
                    collection_date=collection_date,
                ),
            ]

            await asyncio.gather(*tasks)

            print("Completed pipeline runs")


def handler(event, context) -> None:
    access_token = "BQB62-q8NjI9_0rrQCjQdb8asnv-Tg0Vw6gwGvwLv-zWQvBcUOvI5s8gTE6YJrUIboIi0qu65S2GqjRII2EDxXcW9fyPjmK5R2wyGVKGJA7_0w6P1W6m8EWFPkoImugoBbOIH8Cu2Y0va3glw-aRH78BJyaJoFaA9mvKLm_nKTIdDkCWCCIlttm95_O8ZjBldsbCHayEfl9irYcIYXZZh1M7W8ui0OF-tkApLp4lETGSW0PW4hha4hZd"
    time_range = TimeRange.SHORT_TERM
    collection_date = date.today()

    asyncio.run(main(access_token=access_token, time_range=time_range, collection_date=collection_date))
    

handler("", "")
