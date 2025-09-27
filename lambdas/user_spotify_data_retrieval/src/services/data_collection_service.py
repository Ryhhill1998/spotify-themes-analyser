import asyncio
import datetime
import httpx

from src.core.config import Settings
from src.core.db import get_db_session
from src.models.enums import TimeRange
from src.orchestrators.data_collection_orchestrator import DataCollectionOrchestrator


class DataCollectionService:
    """Service for executing data collection operations"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.lyrics_semaphore = asyncio.Semaphore(
            settings.lyrics_max_concurrent_scrapes
        )
        self.orchestrator = DataCollectionOrchestrator(settings, self.lyrics_semaphore)

    async def collect_user_data(
        self,
        access_token: str,
        time_range: TimeRange,
        collection_date: datetime.date,
    ) -> None:
        """Collect user data using the orchestrator"""
        async with httpx.AsyncClient() as client:
            with get_db_session(self.settings.db_connection_string) as db_session:
                await self.orchestrator.run_data_collection_pipeline(
                    client=client,
                    db_session=db_session,
                    access_token=access_token,
                    time_range=time_range,
                    collection_date=collection_date,
                )
