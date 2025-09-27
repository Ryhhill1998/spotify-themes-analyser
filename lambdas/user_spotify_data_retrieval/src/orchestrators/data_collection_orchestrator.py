import asyncio
import datetime
import httpx
import sqlalchemy

from src.core.config import Settings
from src.factories.pipeline_factory import PipelineFactory
from src.models.enums import TimeRange
from src.pipelines.profile_pipeline import ProfilePipeline
from src.pipelines.top_artists_pipeline import TopArtistsPipeline
from src.pipelines.top_tracks_pipeline import TopTracksPipeline
from src.pipelines.top_genres_pipeline import TopGenresPipeline
from src.pipelines.top_emotions_pipeline import TopEmotionsPipeline
from src.services.emotional_profiles.model_service import ModelService
from src.services.lyrics.lyrics_scraper import LyricsScraper
from src.services.spotify_service import SpotifyService


class DataCollectionOrchestrator:
    """Orchestrates the execution of data collection pipelines"""
    
    def __init__(self, settings: Settings, lyrics_semaphore: asyncio.Semaphore):
        self.settings = settings
        self.lyrics_semaphore = lyrics_semaphore
    
    async def run_top_artists_and_genres_pipelines(
        self,
        top_artists_pipeline: TopArtistsPipeline,
        top_genres_pipeline: TopGenresPipeline,
        access_token: str,
        user_id: str,
        time_range: TimeRange,
        collection_date: datetime.date,
    ) -> None:
        """Run top artists and genres pipelines"""
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
        self,
        top_tracks_pipeline: TopTracksPipeline,
        top_emotions_pipeline: TopEmotionsPipeline,
        access_token: str,
        user_id: str,
        time_range: TimeRange,
        collection_date: datetime.date,
    ) -> None:
        """Run top tracks and emotions pipelines"""
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
        self,
        client: httpx.AsyncClient,
        db_session: sqlalchemy.orm.Session,
        access_token: str,
        time_range: TimeRange,
        collection_date: datetime.date,
    ) -> None:
        """Run the complete data collection pipeline"""
        spotify_service = SpotifyService(client=client, base_url=self.settings.spotify_base_url)
        lyrics_scraper = LyricsScraper(
            client=client,
            base_url=self.settings.lyrics_base_url,
            headers=self.settings.lyrics_headers,
            semaphore=self.lyrics_semaphore,
        )
        model_service = ModelService(
            api_key=self.settings.model_api_key,
            model=self.settings.model_name,
            temperature=self.settings.model_temp,
            max_tokens=self.settings.model_max_tokens,
            top_p=self.settings.model_top_p,
            instructions=self.settings.model_instructions,
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
            self.run_top_artists_and_genres_pipelines(
                top_artists_pipeline=top_artists_pipeline,
                top_genres_pipeline=top_genres_pipeline,
                access_token=access_token,
                user_id=profile.id,
                time_range=time_range,
                collection_date=collection_date,
            ),
            self.run_top_tracks_and_emotions_pipelines(
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
