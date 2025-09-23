from sqlalchemy.orm import Session

from backend.lambdas.user_spotify_data_retrieval.src.services.emotional_profiles.emotional_profiles_service import (
    EmotionalProfilesService,
)
from backend.lambdas.user_spotify_data_retrieval.src.services.lyrics.lyrics_service import (
    LyricsService,
)
from src.pipelines.top_emotions_pipeline import TopEmotionsPipeline
from src.repositories.top_items.top_emotions_repository import TopEmotionsRepository
from src.repositories.track_emotional_profiles_repository import (
    TrackEmotionalProfilesRepository,
)
from src.repositories.track_lyrics_repository import TrackLyricsRepository
from backend.lambdas.user_spotify_data_retrieval.src.services.emotional_profiles.model_service import (
    ModelService,
)
from backend.lambdas.user_spotify_data_retrieval.src.services.lyrics.lyrics_scraper import (
    LyricsScraper,
)
from src.pipelines.top_genres_pipeline import TopGenresPipeline
from src.repositories.top_items.top_genres_repository import TopGenresRepository
from src.pipelines.profile_pipeline import ProfilePipeline
from src.pipelines.top_artists_pipeline import TopArtistsPipeline
from src.pipelines.top_tracks_pipeline import TopTracksPipeline
from src.repositories.artists_repository import ArtistsRepository
from src.repositories.profile_repository import ProfileRepository
from src.repositories.top_items.top_artists_repository import TopArtistsRepository
from src.repositories.top_items.top_tracks_repository import TopTracksRepository
from src.repositories.tracks_repository import TracksRepository
from src.services.spotify_service import SpotifyService


class PipelineFactory:
    def __init__(
        self,
        spotify_service: SpotifyService,
        db_session: Session,
        lyrics_scraper: LyricsScraper,
        model_service: ModelService,
    ):
        self.spotify_service = spotify_service
        self.db_session = db_session
        self.lyrics_scraper = lyrics_scraper
        self.model_service = model_service

    def create_profile_pipeline(self) -> ProfilePipeline:
        return ProfilePipeline(
            spotify_service=self.spotify_service,
            profile_repository=ProfileRepository(self.db_session),
        )

    def create_top_artists_pipeline(self) -> TopArtistsPipeline:
        return TopArtistsPipeline(
            spotify_service=self.spotify_service,
            artists_repository=ArtistsRepository(self.db_session),
            top_artists_repository=TopArtistsRepository(self.db_session),
        )

    def create_top_tracks_pipeline(self) -> TopTracksPipeline:
        return TopTracksPipeline(
            spotify_service=self.spotify_service,
            artists_repository=ArtistsRepository(self.db_session),
            tracks_repository=TracksRepository(self.db_session),
            top_tracks_repository=TopTracksRepository(self.db_session),
        )

    def create_top_genres_pipeline(self) -> TopGenresPipeline:
        return TopGenresPipeline(
            top_genres_repository=TopGenresRepository(self.db_session)
        )

    def create_top_emotions_pipeline(self) -> TopEmotionsPipeline:
        lyrics_service = LyricsService(
            lyrics_repository=TrackLyricsRepository(self.db_session),
            lyrics_scraper=self.lyrics_scraper,
        )
        emotional_profile_service = EmotionalProfilesService(
            emotional_profile_repository=TrackEmotionalProfilesRepository(
                self.db_session
            ),
            model_service=self.model_service,
        )
        return TopEmotionsPipeline(
            lyrics_service=lyrics_service,
            emotional_profile_service=emotional_profile_service,
            top_emotions_repository=TopEmotionsRepository(self.db_session),
        )
