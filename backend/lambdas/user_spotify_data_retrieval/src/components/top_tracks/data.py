from src.shared.spotify.enums import TimeRange
from src.shared.spotify.top_items_service import ItemType, SpotifyTopItemsService
from src.components.top_tracks.models.domain import SpotifyTrack, TopTrack
from httpx import AsyncClient


class SpotifyTopTracksService(SpotifyTopItemsService):
    def __init__(self, client: AsyncClient, base_url: str):
        super().__init__(client=client, base_url=base_url, item_type=ItemType.ARTISTS)

    async def get_top_tracks(self, access_token: str, time_range: TimeRange, limit: int = 50) -> list[TopTrack]:
        items = await self._get_top_items_data(access_token=access_token, time_range=time_range, limit=limit)

        # validate data format
        spotify_tracks = [SpotifyTrack(**item) for item in items]
        top_tracks = [
            TopTrack.from_spotify_track(track, position=index + 1) 
            for index, track in enumerate(spotify_tracks)
        ]

        return top_tracks
        