from httpx import AsyncClient

from src.mappers.spotify_to_dto import convert_spotify_profile_to_dto
from src.models.spotify import SpotifyProfile, SpotifyArtist, SpotifyTrack
from src.models.dto import Profile, Artist, Track


class SpotifyService:
    def __init__(self, client: AsyncClient, base_url: str):
        self.client = client
        self.base_url = base_url

    @staticmethod
    def _get_bearer_auth_headers(access_token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {access_token}"}
    
    async def _get_data_from_api(
        self, url: str, headers: dict[str, str], params: dict | None
    ) -> dict:
        response = self.client.get(url=url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    
    async def get_user_profile(self, access_token: str) -> Profile:
        url = f"{self.base_url}/me"
        headers = self._get_bearer_auth_headers(access_token)
        data = await self._get_data_from_api(url=url, headers=headers)
        spotify_profile = SpotifyProfile.model_validate(data)
        profile = convert_spotify_profile_to_dto(spotify_profile)

        return profile

    async def get_user_top_artists(
        self, access_token: str, time_range: str, limit: int = 50
    ) -> list[Artist]:
        url = f"{self.base_url}/me/top/artists"
        headers = self._get_bearer_auth_headers(access_token)
        params = {"time_range": time_range, "limit": limit}
        data = await self._get_data_from_api(url=url, headers=headers, params=params)
        items = data.get("items", [])
        spotify_artists = [SpotifyArtist.model_validate(item) for item in items]
        artists = [
            Artist(
                id=artist.id,
                name=artist.name,
                images=[img.model_dump() for img in artist.images],
                spotify_url=artist.external_urls.spotify,
                genres=artist.genres,
                followers=artist.followers.total,
                popularity=artist.popularity,
            ) 
            for artist in spotify_artists
        ]

        return artists

    async def get_user_top_tracks(
        self, access_token: str, time_range: str, limit: int = 50
    ) -> list[Track]:
        url = f"{self.base_url}/me/top/tracks"
        headers = self._get_bearer_auth_headers(access_token)
        params = {"time_range": time_range, "limit": limit}
        data = await self._get_data_from_api(url=url, headers=headers, params=params)
        items = data.get("items", [])
        spotify_tracks = [SpotifyTrack.model_validate(item) for item in items]
        tracks = [
            Track(
                id=track.id,
                name=track.name,
                images=[img.model_dump() for img in track.album.images],
                spotify_url=track.external_urls.spotify,
                release_date=track.album.release_date,
                explicit=track.explicit,
                duration_ms=track.duration_ms,
                popularity=track.popularity,
                artists=[artist.model_dump() for artist in track.artists],
            ) 
            for track in spotify_tracks
        ]

        return tracks
