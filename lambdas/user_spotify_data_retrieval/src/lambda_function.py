from datetime import date
import httpx
import asyncio
import json
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, BeforeValidator
from typing import Dict, Any, Annotated

from src.pipelines.top_emotions_pipeline import TopEmotionsPipeline
from src.services.emotional_profiles.model_service import ModelService
from src.services.lyrics.lyrics_scraper import LyricsScraper
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

lyrics_semaphore = asyncio.Semaphore(settings.lyrics_max_concurrent_scrapes)


class RunConfig(BaseModel):
    """Configuration for running the data collection pipeline"""
    access_token: str = Field(..., min_length=1)
    time_range: Annotated[TimeRange, BeforeValidator(lambda v: TimeRange(v))] = Field(default=TimeRange.SHORT_TERM)
    collection_date: Annotated[date, BeforeValidator(lambda v: date.fromisoformat(v))] = Field(default_factory=date.today)


def parse_event(event: Dict[str, Any]) -> RunConfig:
    if "Records" in event and len(event["Records"]) > 0:
        message_body = event["Records"][0]["body"]
        
        try:
            body_data = json.loads(message_body)
            return RunConfig.model_validate(body_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in SQS message body: {e}")
    else:
        # Fallback for direct Lambda invocation (non-SQS)
        return RunConfig.model_validate(event)


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
        user_id=user_id,
        time_range=time_range,
        collection_date=collection_date,
        artists=top_artists,
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
        user_id=user_id,
        time_range=time_range,
        collection_date=collection_date,
        tracks=top_tracks,
    )


async def run_data_collection_pipeline(
    client: httpx.AsyncClient,
    db_session: Session,
    access_token: str,
    settings: Settings,
    time_range: TimeRange,
    collection_date: date,
) -> None:
    spotify_service = SpotifyService(client=client, base_url=settings.spotify_base_url)
    lyrics_scraper = LyricsScraper(
        client=client,
        base_url=settings.lyrics_base_url,
        headers=settings.lyrics_headers,
        semaphore=lyrics_semaphore,
    )
    model_service = ModelService(
        api_key=settings.model_api_key,
        model=settings.model_name,
        temperature=settings.model_temp,
        max_tokens=settings.model_max_tokens,
        top_p=settings.model_top_p,
        instructions=settings.model_instructions,
    )

    pipeline_factory = PipelineFactory(
        spotify_service=spotify_service,
        db_session=db_session,
        lyrics_scraper=lyrics_scraper,
        model_service=model_service,
    )

    profile_pipeline: ProfilePipeline = pipeline_factory.create_profile_pipeline()
    top_artists_pipeline: TopArtistsPipeline = (
        pipeline_factory.create_top_artists_pipeline()
    )
    top_tracks_pipeline: TopTracksPipeline = (
        pipeline_factory.create_top_tracks_pipeline()
    )
    top_genres_pipeline: TopGenresPipeline = (
        pipeline_factory.create_top_genres_pipeline()
    )
    top_emotions_pipeline: TopEmotionsPipeline = (
        pipeline_factory.create_top_emotions_pipeline()
    )

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


async def main(access_token: str, time_range: TimeRange, collection_date: date) -> None:
    async with httpx.AsyncClient() as client:
        with get_db_session(settings.db_connection_string) as db_session:
            await run_data_collection_pipeline(
                client=client,
                db_session=db_session,
                access_token=access_token,
                settings=settings,
                time_range=time_range,
                collection_date=collection_date,
            )


def handler(event, context) -> None:
    config: RunConfig = parse_event(event)
    
    asyncio.run(
        main(
            access_token=config.access_token,
            time_range=config.time_range,
            collection_date=config.collection_date,
        )
    )
