from src.components.top_artists.service import TopArtistsService
from src.components.top_artists.repository import TopArtistsRepository
from src.core.db import SessionLocal


def get_top_artists_service() -> TopArtistsService:
    db_session = SessionLocal()
    repository = TopArtistsRepository(db_session)
    top_artists_service = TopArtistsService(repository)

    return top_artists_service
    

__all__ = ["get_top_artists_service"]
