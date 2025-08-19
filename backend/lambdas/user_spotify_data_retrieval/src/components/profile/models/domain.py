from pydantic import BaseModel

from src.shared.models.domain import SpotifyImage, SpotifyProfileFollowers


class SpotifyProfile(BaseModel):
    id: str
    display_name: str
    email: str | None = None
    href: str
    images: list[SpotifyImage]
    followers: SpotifyProfileFollowers

    def __repr__(self) -> str:
        return f"<Profile(name={self.display_name}, email={self.email})>"
    

class Profile(BaseModel):
    id: str
    display_name: str
    email: str | None = None
    href: str
    images: list[SpotifyImage]
    followers: int

    @classmethod
    def from_spotify_profile(cls, profile: SpotifyProfile) -> "Profile":
        return cls(
            id=profile.id,
            name=profile.display_name,
            email=profile.email,
            href=profile.href,
            images=profile.images,
            followers=profile.followers.total,
        )
