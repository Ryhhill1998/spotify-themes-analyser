import asyncio
from itertools import batched
from httpx import AsyncClient

from src.models.enums import TimeRange
from src.models.spotify import SpotifyProfile, SpotifyArtist, SpotifyTrack
from src.models.domain import Image, Profile, Artist, Track


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
    
    def _spotify_profile_to_profile(spotify_profile: SpotifyProfile) -> Profile:
        return Profile(
            id=spotify_profile.id,
            display_name=spotify_profile.display_name,
            email=spotify_profile.email,
            href=spotify_profile.href,
            images=spotify_profile.images,
            followers=spotify_profile.followers.total
        )
    
    async def get_user_profile(self, access_token: str) -> Profile:
        url = f"{self.base_url}/me"
        headers = self._get_bearer_auth_headers(access_token)
        data = await self._get_data_from_api(url=url, headers=headers)

        spotify_profile = SpotifyProfile.model_validate(data)
        profile = self._spotify_profile_to_profile(spotify_profile)

        return profile
    
    def _spotify_artist_to_artist(spotify_artist: SpotifyArtist) -> Artist:
        Artist(
            id=spotify_artist.id,
            name=spotify_artist.name,
            images=spotify_artist.images,
            spotify_url=spotify_artist.external_urls.spotify,
            genres=spotify_artist.genres,
            followers=spotify_artist.followers.total,
            popularity=spotify_artist.popularity,
        ) 

    async def get_user_top_artists(
        self, access_token: str, time_range: TimeRange, limit: int = 50
    ) -> list[Artist]:
        url = f"{self.base_url}/me/top/artists"
        headers = self._get_bearer_auth_headers(access_token)
        params = {"time_range": time_range.value, "limit": limit}
        data = await self._get_data_from_api(url=url, headers=headers, params=params)

        items = data.get("items", [])
        spotify_artists = [SpotifyArtist.model_validate(item) for item in items]
        artists = [self._spotify_artist_to_artist(artist) for artist in spotify_artists]

        return artists
    
    def _spotify_track_to_track(spotify_track: SpotifyTrack) -> Track:
        Track(
            id=spotify_track.id,
            name=spotify_track.name,
            images=[
                Image(height=image.height, width=image.width, url=image.url) 
                for image in spotify_track.album.images
            ],
            spotify_url=spotify_track.external_urls.spotify,
            album_name=spotify_track.album.name,
            release_date=spotify_track.album.release_date,
            explicit=spotify_track.explicit,
            duration_ms=spotify_track.duration_ms,
            popularity=spotify_track.popularity,
            artist_ids=[artist.id for artist in spotify_track.artists],
        ) 

    async def get_user_top_tracks(
        self, access_token: str, time_range: TimeRange, limit: int = 50
    ) -> list[Track]:
        url = f"{self.base_url}/me/top/tracks"
        headers = self._get_bearer_auth_headers(access_token)
        params = {"time_range": time_range.value, "limit": limit}
        data = await self._get_data_from_api(url=url, headers=headers, params=params)

        items = data.get("items", [])
        spotify_tracks = [SpotifyTrack.model_validate(item) for item in items]
        tracks = [self._spotify_track_to_track(track) for track in spotify_tracks]

        return tracks

    async def _get_artists_by_ids(self, access_token: str, artist_ids: list[str]) -> list[Artist]:
        url = f"{self.base_url}/artists"
        headers = self._get_bearer_auth_headers(access_token)
        params = {"ids": ",".join(artist_ids)}
        data = await self._get_data_from_api(url=url, headers=headers, params=params)

        items = data.get("items", [])
        spotify_artists = [SpotifyArtist.model_validate(item) for item in items]
        artists = [self._spotify_artist_to_artist(artist) for artist in spotify_artists]

        return artists
    
    async def get_artists_by_ids(self, access_token: str, artist_ids: list[str]) -> list[Artist]:
        batched_artist_ids = list(batched(artist_ids, SpotifyService.BATCH_SIZE))
        tasks = [
            self._get_artists_by_ids(access_token=access_token, artist_ids=batch)
            for batch in batched_artist_ids
        ]
        results = await asyncio.gather(*tasks)
        artists = [artist for batch in results for artist in batch] 
        
        return artists
