from datetime import date
from src.models.dto import TopTrack, Track
from src.models.enums import TimeRange
from src.repositories.artists_repository import ArtistsRepository
from src.repositories.top_items.top_artists_repository import TopArtistsRepository
from src.repositories.top_items.top_tracks_repository import TopTracksRepository
from src.repositories.tracks_repository import TracksRepository
from src.services.spotify_service import SpotifyService


class TopTracksPipeline:
    def __init__(
        self, 
        spotify_service: SpotifyService,
        artists_repository: ArtistsRepository,
        tracks_repository: TracksRepository,
        top_artists_repository: TopArtistsRepository,
        top_tracks_repository: TopTracksRepository,
    ):
        self.spotify_service = spotify_service
        self.artists_repository = artists_repository
        self.tracks_repository = tracks_repository
        self.top_artists_repository = top_artists_repository
        self.top_tracks_repository = top_tracks_repository

    async def run(
        self, access_token: str, user_id: str, time_range: TimeRange, collection_date: date
    ) -> list[Track]:
        # 1. Get top tracks from Spotify API
        tracks = await self.spotify_service.get_user_top_tracks(access_token=access_token, time_range=time_range)

        # 2. Extract unique artist ids from tracks
        unique_artist_ids = set(artist.id for track in tracks for artist in track.artists)

        # 3. Get full artist details from Spotify API
        artists = await self.spotify_service.get_artists_by_ids(access_token=access_token, artist_ids=list(unique_artist_ids))

        # 4. Persist artists to DB (if not already present)
        self.artists_repository.upsert_many(artists)

        # 5. Enrich tracks with full artist details
        # 6. Persist tracks to DB (if not already present)
        # 7. Create TopTrack DTOs, calculate position changes, and persist to DB
        # 8. Return the list of tracks

        pass
        # tracks = await self.spotify_service.get_user_top_tracks(access_token=access_token, time_range=time_range)

        # # 2. Extract unique artists from tracks and persist to DB (if not already present)
        # unique_artists = set(artist for track in tracks for artist in track.artists)
        # self.artists_repository.upsert_many(list(unique_artists))

        # # 3. Persist tracks to DB (if not already present)
        # self.tracks_repository.upsert_many(tracks)

        # # 4. Create TopTrack DTOs, calculate position changes, and persist to DB
        # top_tracks = [
        #     TopTrack(
        #         user_id=user_id,
        #         track_id=track.id,
        #         collection_date=collection_date,
        #         time_range=time_range,
        #         position=index + 1,
        #     )
        #     for index, track in enumerate(tracks)
        # ]
        # previous_top_tracks = self.top_tracks_repository.get_previous_top_tracks(user_id=user_id, time_range=time_range)
        # calculate_position_changes(previous_items=previous_top_tracks, current_items=top_tracks)
        # self.top_tracks_repository.add_many(top_tracks)

        # # 5. Return the list of tracks
        # return tracks
