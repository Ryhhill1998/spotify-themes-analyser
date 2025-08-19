from datetime import date
from src.components.top_tracks.models.db import TrackDB
from src.shared.models.db import TopItemDBMixin, track_artist_association_table
from src.components.top_artists.models.domain import TopArtist
from src.shared.spotify.enums import TimeRange
from sqlalchemy import ForeignKey, String, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.shared.db import Base


class ArtistDB(Base):
    __tablename__ = "artist"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    images: Mapped[list[dict[str, int | str]]] = mapped_column(JSON, nullable=True)
    spotify_url: Mapped[str] = mapped_column(String, nullable=False)
    genres: Mapped[list[str]] = mapped_column(JSON, nullable=True)
    followers: Mapped[int] = mapped_column(Integer, nullable=False)
    popularity: Mapped[int] = mapped_column(Integer, nullable=False)

    tracks: Mapped[list["TrackDB"]] = relationship(
        "TrackDB", 
        secondary=track_artist_association_table, 
        back_populates="artists"
    )
    
    @classmethod
    def from_top_artist(cls, top_artist: TopArtist) -> "ArtistDB":
        return cls(
            id=top_artist.id,
            name=top_artist.name,
            images=[image.dict() for image in top_artist.images],
            spotify_url=top_artist.spotify_url,
            genres=top_artist.genres,
            followers=top_artist.followers,
            popularity=top_artist.popularity,
        )


class TopArtistDB(TopItemDBMixin, Base):
    __tablename__ = "top_artist"

    artist_id: Mapped[str] = mapped_column(String, ForeignKey("artists.id", ondelete="CASCADE"), primary_key=True)

    # relationship to Artist
    artist: Mapped[ArtistDB] = relationship()

    @property
    def item_id(self) -> str:
        return self.artist_id
    
    @classmethod
    def from_top_artist(cls, user_id: str, top_artist: TopArtist, time_range: TimeRange, collection_date: date) -> "TopArtistDB":
        return cls(
            user_id=user_id,
            artist_id=top_artist.id,
            time_range=time_range,
            collection_date=collection_date,
            position=top_artist.position,
            position_change=top_artist.position_change,
        )
