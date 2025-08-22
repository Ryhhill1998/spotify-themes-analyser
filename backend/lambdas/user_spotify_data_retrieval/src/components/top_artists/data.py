from src.shared.spotify.enums import TimeRange
from src.shared.spotify.top_items_service import ItemType, SpotifyTopItemsDataService
from src.components.top_artists.models.domain import SpotifyArtist, TopArtist
from httpx import AsyncClient


class TopArtistsDataService(SpotifyTopItemsDataService):
    def __init__(self, client: AsyncClient, base_url: str):
        super().__init__(client=client, base_url=base_url, item_type=ItemType.ARTISTS)

    async def get_top_artists(self, access_token: str, time_range: TimeRange, limit: int = 50) -> list[TopArtist]:
        items = await self._get_top_items_data(access_token=access_token, time_range=time_range, limit=limit)

        # validate data format
        spotify_artists = [SpotifyArtist(**item) for item in items]
        top_artists = [
            TopArtist.from_spotify_artist(artist, position=index + 1) 
            for index, artist in enumerate(spotify_artists)
        ]

        return top_artists
        