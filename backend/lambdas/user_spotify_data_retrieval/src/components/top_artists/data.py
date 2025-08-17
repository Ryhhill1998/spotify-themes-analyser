from src.components.top_artists.models.domain import SpotifyArtist, TopArtist
from httpx import AsyncClient


class TopArtistsFetcher:
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
    
    async def _get_top_artists_data(self, access_token: str, time_range: str, limit: int = 50) -> dict:
        data = await self._get_data_from_api(
            endpoint="me/top/artists", access_token=access_token, params={"time_range": time_range, "limit": limit}
        )

        if not data or "items" not in data:
            raise ValueError("No top artists found or invalid response format.")

        items = data.get("items", [])

        return items

    async def get_top_artists(self, access_token: str, time_range: str, limit: int = 50) -> list:
        items = await self._get_top_artists_data(access_token=access_token, time_range=time_range, limit=limit)

        # validate data format
        spotify_artists = [SpotifyArtist(**item) for item in items]
        top_artists = [TopArtist.from_spotify_artist(artist) for artist in spotify_artists]

        return top_artists
        