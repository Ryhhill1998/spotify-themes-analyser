from src.components.top_artists.manager import TopArtistsManager
from src.components.top_artists.repository import TopArtistsRepository
from backend.shared.db import SessionLocal


def get_top_artists_manager() -> TopArtistsManager:
    db_session = SessionLocal()
    repository = TopArtistsRepository(db_session)
    top_artists_service = TopArtistsManager(repository)

    return top_artists_service
    

__all__ = ["get_top_artists_manager"]
