from httpx import AsyncClient
from enum import Enum


class TimeRange(Enum):
    SHORT_TERM = "short_term"
    MEDIUM_TERM = "medium_term"
    LONG_TERM = "long_term"


class SpotifyDataService:
    def __init__(self, client: AsyncClient, base_url: str):
        self.client = client
        self.base_url = base_url

    @staticmethod
    def _get_bearer_auth_headers(access_token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {access_token}"}
    
    async def _get_data_from_api(self, endpoint: str, access_token: str, params: dict) -> dict:
        url = f"{self.base_url}/{endpoint}"
        response = await self.client.get(url, headers=self._get_bearer_auth_headers(access_token), params=params)

        if response.status_code != 200:
            raise Exception(f"Failed to retrieve data: {response.text}")

        return response.json()
