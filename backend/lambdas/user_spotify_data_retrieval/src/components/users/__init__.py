from src.components.users.data import SpotifyUserService
from src.components.users.orchestrator import UserOrchestrator
from src.components.users.repository import UserRepository
from src.shared.spotify.config import SpotifySettings
from src.shared.spotify.client import spotify_client
from backend.shared.db import SessionLocal


def get_user_orchestrator() -> UserOrchestrator:
    db_session = SessionLocal()
    spotify_settings = SpotifySettings()
    data = SpotifyUserService(client=spotify_client, base_url=spotify_settings.base_url)
    repository = UserRepository(db_session)
    user_orchestrator = UserOrchestrator(data=data, repository=repository)

    return user_orchestrator
    

__all__ = ["get_user_orchestrator"]
