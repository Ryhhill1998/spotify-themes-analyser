from datetime import date
from src.components.top_tracks.models.domain import TopTrack
from src.components.top_tracks.data import SpotifyTopTracksService
from src.components.top_tracks.repository import TopTracksRepository


class TopTracksOrchestrator:
    def __init__(self, data: SpotifyTopTracksService, repository: TopTracksRepository):
        self.data = data
        self.repository = repository

    async def get_and_store_top_tracks(self, user_id: str, access_token: str, time_range: str, collection_date: date) -> list[TopTrack]:
        top_tracks = await self.data.get_top_tracks(access_token=access_token, time_range=time_range)
        previous_top_tracks = self.repository.get_previous_top_tracks(user_id=user_id, time_range=time_range)

        if previous_top_tracks:
            self._calculate_and_populate_position_change(
                previous_top_items=previous_top_tracks, current_top_items=top_tracks
            )

        self.repository.store_top_tracks(user_id=user_id, top_tracks=top_tracks, time_range=time_range, collection_date=collection_date)

        return top_tracks
        