import asyncio
from loguru import logger
from src.models.domain import TrackLyrics, TrackLyricsRequest
from src.repositories.track_lyrics_repository import TrackLyricsRepository
from src.services.lyrics.lyrics_scraper import LyricsScraper


class LyricsServiceException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class LyricsService:
    def __init__(
        self,
        lyrics_repository: TrackLyricsRepository,
        lyrics_scraper: LyricsScraper,
    ):
        self.lyrics_repository = lyrics_repository
        self.lyrics_scraper = lyrics_scraper

    async def _scrape_lyrics(self, request: TrackLyricsRequest) -> TrackLyrics:
        lyrics = await self.lyrics_scraper.get_lyrics(
            artist_name=request.track_artist, track_title=request.track_name
        )
        return TrackLyrics(track_id=request.track_id, lyrics=lyrics)

    async def _scrape_many_lyrics(
        self, lyrics_requests: list[TrackLyricsRequest]
    ) -> list[TrackLyrics]:
        tasks = [self._scrape_lyrics(request) for request in lyrics_requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful_results = []
        for request, result in zip(lyrics_requests, results):
            if isinstance(result, TrackLyrics):
                successful_results.append(result)
            elif isinstance(result, Exception):
                logger.warning(
                    f"Failed to scrape lyrics for {request.track_artist} - {request.track_name}: {result}"
                )

        if not successful_results:
            raise LyricsServiceException("No lyrics were successfully scraped")

        return successful_results

    async def get_many_lyrics(
        self, lyrics_requests: list[TrackLyricsRequest]
    ) -> list[TrackLyrics]:
        # Check which lyrics are already in the DB
        track_ids = set(request.track_id for request in lyrics_requests)
        existing_track_lyrics = self.lyrics_repository.get_many(track_ids)
        track_ids -= set(lyric.track_id for lyric in existing_track_lyrics)

        # Determine which requests need to be scraped
        lyrics_requests = [
            request for request in lyrics_requests if request.track_id in track_ids
        ]

        # Scrape missing lyrics
        new_track_lyrics = await self._scrape_many_lyrics(lyrics_requests)

        # Store newly scraped lyrics in the DB
        self.lyrics_repository.add_many(new_track_lyrics)

        # Combine existing and newly scraped lyrics
        return [*existing_track_lyrics, *new_track_lyrics]
