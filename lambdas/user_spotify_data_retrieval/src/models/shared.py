from pydantic import BaseModel


class Image(BaseModel):
    height: int
    width: int
    url: str


class TrackArtist(BaseModel):
    id: str
    name: str
    