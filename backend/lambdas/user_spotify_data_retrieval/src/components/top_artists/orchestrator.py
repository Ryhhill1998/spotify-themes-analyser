from datetime import date
from src.components.top_artists.models.domain import TopArtist
from src.components.top_artists.data import SpotifyTopArtistsService
from src.components.top_artists.repository import TopArtistsRepository


class TopArtistsOrchestrator:
    def __init__(self, data: SpotifyTopArtistsService, repository: TopArtistsRepository):
        self.data = data
        self.repository = repository

    async def get_and_store_top_artists(self, user_id: str, access_token: str, time_range: str, collection_date: date) -> list[TopArtist]:
        top_artists = await self.data.get_top_artists(access_token=access_token, time_range=time_range)
        previous_top_artists = self.repository.get_previous_top_artists(user_id=user_id, time_range=time_range)

        if previous_top_artists:
            self._calculate_and_populate_position_change(
                previous_top_items=previous_top_artists, current_top_items=top_artists
            )

        self.repository.store_top_artists(user_id=user_id, top_artists=top_artists, time_range=time_range, collection_date=collection_date)

        return top_artists
        