from src.shared.spotify_data_service import SpotifyDataService
from src.components.top_artists.models.domain import SpotifyArtist, TopArtist
from httpx import AsyncClient
from enum import Enum


class TimeRange(Enum):
    SHORT_TERM = "short_term"
    MEDIUM_TERM = "medium_term"
    LONG_TERM = "long_term"


class TopArtistsFetcher(SpotifyDataService):
    def __init__(self, client: AsyncClient, base_url: str):
        super().__init__(client=client, base_url=base_url)
    
    async def _get_top_artists_data(self, access_token: str, time_range: TimeRange, limit: int = 50) -> dict:
        data = await self._get_data_from_api(
            endpoint="me/top/artists", access_token=access_token, params={"time_range": time_range.value, "limit": limit}
        )

        if not data or "items" not in data:
            raise ValueError("No top artists found or invalid response format.")

        items = data.get("items", [])

        return items

    async def get_top_artists(self, access_token: str, time_range: TimeRange, limit: int = 50) -> list:
        items = await self._get_top_artists_data(access_token=access_token, time_range=time_range, limit=limit)

        # validate data format
        spotify_artists = [SpotifyArtist(**item) for item in items]
        top_artists = [TopArtist.from_spotify_artist(artist) for artist in spotify_artists]

        return top_artists
        