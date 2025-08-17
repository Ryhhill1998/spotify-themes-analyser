from httpx import AsyncClient


class TopArtistsDataRetriever:
    def __init__(self, client: AsyncClient, client_id: str, client_secret: str, base_url: str):
        self.client = client
        self.client_id = client_id
        self.client_secret = client_secret
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

    async def get_top_artists(self, access_token: str, time_range: str, limit: int = 50) -> list:
        data = await self._get_data_from_api(
            endpoint="me/top/artists", access_token=access_token, params={"time_range": time_range, "limit": limit}
        )

        if not data or "items" not in data:
            raise ValueError("No top artists found or invalid response format.")

        return data.get("items", [])
        