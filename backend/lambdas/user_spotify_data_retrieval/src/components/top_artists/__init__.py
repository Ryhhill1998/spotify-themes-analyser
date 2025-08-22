from src.shared.spotify.config import SpotifySettings
from src.shared.spotify.client import spotify_client
from src.components.top_artists.data import TopArtistsDataService
from src.components.top_artists.repository import TopArtistsRepository
from src.components.top_artists.orchestrator import TopArtistsOrchestrator
from backend.shared.db import SessionLocal


def get_top_artists_orchestrator() -> TopArtistsOrchestrator:
    db_session = SessionLocal()
    spotify_settings = SpotifySettings()
    data = TopArtistsDataService(client=spotify_client, base_url=spotify_settings.base_url)
    repository = TopArtistsRepository(db_session)
    top_artists_orchestrator = TopArtistsOrchestrator(data=data, repository=repository)

    return top_artists_orchestrator
    

__all__ = ["get_top_artists_orchestrator"]
