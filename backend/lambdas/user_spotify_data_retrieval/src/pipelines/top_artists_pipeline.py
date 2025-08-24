from datetime import date
from src.models.dto import Artist, TopArtist
from src.models.enums import TimeRange
from src.repositories.artist_repo import ArtistRepository
from src.services.spotify_service import SpotifyService


class TopArtistsPipeline:
    def __init__(self, spotify_service: SpotifyService, artist_repo: ArtistRepository):
        self.spotify_service = spotify_service
        self.artist_repo = artist_repo

    async def run(
        self, access_token: str, user_id: str, time_range: TimeRange, collection_date: date
    ) -> list[Artist]:
        artists = await self.spotify_service.get_user_top_artists(access_token=access_token, time_range=time_range)
        top_artists = [
            TopArtist(
                user_id=user_id,
                artist_id=artist.id,
                collection_date=collection_date,
                time_range=time_range,
                position=index + 1,
                position_change=None,
            )
            for index, artist in enumerate(artists)
        ]
        self.artist_repo.upsert_many(artists)

        return artists
    