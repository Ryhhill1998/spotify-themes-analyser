import asyncio
from itertools import batched
from httpx import AsyncClient

from src.models.enums import TimeRange
from backend.lambdas.user_spotify_data_retrieval.src.models.domain import SpotifyProfileAPI, SpotifyProfile, SpotifyArtistAPI, SpotifyArtist, SpotifyTrackArtist, SpotifyTrackAPI, SpotifyTrack


class SpotifyService:
    BATCH_SIZE = 50

    def __init__(self, client: AsyncClient, base_url: str):
        self.client = client
        self.base_url = base_url

    @staticmethod
    def _get_bearer_auth_headers(access_token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {access_token}"}
    
    async def _get_data_from_api(
        self, url: str, headers: dict[str, str], params: dict | None
    ) -> dict:
        response = await self.client.get(url=url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    
    async def get_user_profile(self, access_token: str) -> SpotifyProfile:
        url = f"{self.base_url}/me"
        headers = self._get_bearer_auth_headers(access_token)
        data = await self._get_data_from_api(url=url, headers=headers)

        profile_data = SpotifyProfileAPI.model_validate(data)
        profile = SpotifyProfile(
            id=profile_data.id,
            display_name=profile_data.display_name,
            email=profile_data.email,
            href=profile_data.href,
            images=profile_data.images,
            followers=profile_data.followers.total
        )

        return profile

    async def get_user_top_artists(
        self, access_token: str, time_range: TimeRange, limit: int = 50
    ) -> list[SpotifyArtist]:
        url = f"{self.base_url}/me/top/artists"
        headers = self._get_bearer_auth_headers(access_token)
        params = {"time_range": time_range.value, "limit": limit}
        data = await self._get_data_from_api(url=url, headers=headers, params=params)
        items = data.get("items", [])
        artists_data = [SpotifyArtist.model_validate(item) for item in items]
        artists = [
            SpotifyArtist(
                id=artist.id,
                name=artist.name,
                images=artist.images,
                spotify_url=artist.external_urls.spotify,
                genres=artist.genres,
                followers=artist.followers.total,
                popularity=artist.popularity,
            ) 
            for artist in artists_data
        ]

        return artists

    async def get_user_top_tracks(
        self, access_token: str, time_range: TimeRange, limit: int = 50
    ) -> list[SpotifyTrack]:
        url = f"{self.base_url}/me/top/tracks"
        headers = self._get_bearer_auth_headers(access_token)
        params = {"time_range": time_range.value, "limit": limit}
        data = await self._get_data_from_api(url=url, headers=headers, params=params)
        items = data.get("items", [])
        tracks_data = [SpotifyTrack.model_validate(item) for item in items]
        tracks = [
            SpotifyTrack(
                id=track.id,
                name=track.name,
                images=[img.model_dump() for img in track.album.images],
                spotify_url=track.external_urls.spotify,
                release_date=track.album.release_date,
                explicit=track.explicit,
                duration_ms=track.duration_ms,
                popularity=track.popularity,
                artists=[SpotifyTrackArtist(id=artist.id, name=artist.name) for artist in track.artists],
            ) 
            for track in tracks_data
        ]

        return tracks

    async def _get_artists_by_ids(self, access_token: str, artist_ids: list[str]) -> list[SpotifyArtist]:
        url = f"{self.base_url}/artists"
        headers = self._get_bearer_auth_headers(access_token)
        params = {"ids": ",".join(artist_ids)}
        data = await self._get_data_from_api(url=url, headers=headers, params=params)
        items = data.get("items", [])
        artists_data = [SpotifyArtist.model_validate(item) for item in items]
        artists = [
            SpotifyArtist(
                id=artist.id,
                name=artist.name,
                images=artist.images,
                spotify_url=artist.external_urls.spotify,
                genres=artist.genres,
                followers=artist.followers.total,
                popularity=artist.popularity,
            ) 
            for artist in artists_data
        ]

        return artists
    
    async def get_artists_by_ids(self, access_token: str, artist_ids: list[str]) -> list[SpotifyArtist]:
        batched_artist_ids = list(batched(artist_ids, SpotifyService.BATCH_SIZE))
        tasks = [
            self._get_artists_by_ids(access_token=access_token, artist_ids=batch)
            for batch in batched_artist_ids
        ]
        results = await asyncio.gather(*tasks)
        artists = [artist for batch in results for artist in batch] 
        
        return artists
