from pydantic_settings import BaseSettings, SettingsConfigDict


class SpotifySettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SPOTIFY_")

    base_url: str
