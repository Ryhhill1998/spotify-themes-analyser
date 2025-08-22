from src.shared.spotify.config import SpotifySettings
from src.shared.spotify.client import spotify_client
from src.components.top_tracks.data import TopTracksDataService
from src.components.top_tracks.repository import TopTracksRepository
from src.components.top_tracks.orchestrator import TopTracksOrchestrator
from backend.shared.db import SessionLocal


def get_top_tracks_orchestrator() -> TopTracksOrchestrator:
    db_session = SessionLocal()
    spotify_settings = SpotifySettings()
    data = TopTracksDataService(client=spotify_client, base_url=spotify_settings.base_url)
    repository = TopTracksRepository(db_session)
    top_tracks_orchestrator = TopTracksOrchestrator(data=data, repository=repository)

    return top_tracks_orchestrator
    

__all__ = ["get_top_tracks_orchestrator"]
