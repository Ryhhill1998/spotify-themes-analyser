from datetime import date
from src.models.db import ArtistDB
from src.models.domain import SpotifyArtist, TopArtist
from src.mappers.domain_to_db import spotify_artist_to_artist_db
from src.repositories.top_items.top_artists_repository import TopArtistsRepository
from src.utils.calculations import calculate_position_changes
from src.models.enums import TimeRange
from src.repositories.artists_repository import ArtistsRepository
from src.services.spotify_service import SpotifyService


class TopArtistsPipeline:
    def __init__(
        self, 
        spotify_service: SpotifyService, 
        artists_repository: ArtistsRepository, 
        top_artists_repository: TopArtistsRepository,
    ):
        self.spotify_service = spotify_service
        self.artists_repository = artists_repository
        self.top_artists_repository = top_artists_repository

    async def run(
        self, access_token: str, user_id: str, time_range: TimeRange, collection_date: date
    ) -> list[SpotifyArtist]:
        # 1. Get top artists from Spotify API
        spotify_artists: list[SpotifyArtist] = await self.spotify_service.get_user_top_artists(
            access_token=access_token, time_range=time_range
        )

        # 2. Convert to ArtistDB objects
        db_artists: list[ArtistDB] = [spotify_artist_to_artist_db(artist) for artist in spotify_artists]

        # 3. Store in DB
        self.artists_repository.upsert_many(db_artists)

        # 3. Create top artist objects
        top_artists: list[TopArtist] = [
            TopArtist(
                user_id=user_id,
                artist_id=artist.id,
                collection_date=collection_date,
                time_range=time_range,
                position=index + 1,
            )
            for index, artist in enumerate(spotify_artists)
        ]
        previous_top_artists = self.top_artists_repository.get_previous_top_artists(user_id=user_id, time_range=time_range)
        calculate_position_changes(previous_items=previous_top_artists, current_items=top_artists)
        self.top_artists_repository.add_many(top_artists)

        # 4. Return the list of artists
        return artists
    