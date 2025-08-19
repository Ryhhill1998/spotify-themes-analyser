from src.shared.spotify.enums import ItemType, TimeRange
from src.shared.spotify.data_service import SpotifyDataService
from httpx import AsyncClient


class SpotifyTopItemsService(SpotifyDataService):
    def __init__(self, client: AsyncClient, base_url: str, item_type: ItemType):
        super().__init__(client=client, base_url=base_url)
        self.item_type = item_type

    async def _get_top_items_data(self, access_token: str, time_range: TimeRange, limit: int = 50) -> dict:
        data = await self._get_data_from_api(
            endpoint=f"me/top/{self.item_type.value}", 
            access_token=access_token, 
            params={"time_range": time_range.value, "limit": limit},
        )

        if not data or "items" not in data:
            raise ValueError(f"No top {self.item_type.value} found or invalid response format.")

        items = data["items"]

        return items
