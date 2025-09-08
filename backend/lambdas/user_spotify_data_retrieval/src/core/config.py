from pathlib import Path
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    spotify_base_url: str

    db_connection_string: str

    lyrics_base_url: str
    lyrics_user_agent: str
    lyrics_max_concurrent_scrapes: int

    model_api_key: str
    model_name: str
    model_temp: float
    model_max_tokens: int
    model_top_p: float
    model_prompt_path: Path = Field(..., description="Path to prompt file")

    @computed_field
    @property
    def model_instructions(self) -> str:
        return self.model_prompt_path.read_text(encoding="utf-8")
    
    @computed_field
    @property 
    def lyrics_headers(self) -> dict[str, str]:
        return {"User-Agent": self.lyrics_user_agent}
