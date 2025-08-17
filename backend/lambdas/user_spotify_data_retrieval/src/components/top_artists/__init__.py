from src.components.top_artists.data import SpotifyTopArtistsService
from src.components.top_artists.repository import TopArtistsRepository
from src.components.top_artists.orchestrator import TopArtistsOrchestrator
from backend.shared.db import SessionLocal


def get_top_artists_orchestrator() -> TopArtistsOrchestrator:
    db_session = SessionLocal()
    fetcher = SpotifyTopArtistsService()
    repository = TopArtistsRepository(db_session)
    top_artists_service = TopArtistsOrchestrator(fetcher=fetcher, repository=repository)

    return top_artists_service
    

__all__ = ["get_top_artists_orchestrator"]
