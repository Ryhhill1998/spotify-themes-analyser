from datetime import date
from src.shared.spotify.enums import TimeRange
from sqlalchemy import ForeignKey, String, Integer, JSON, Date, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.shared.db import Base


class Artist(Base):
    __tablename__ = "artist"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    images: Mapped[list[str]] = mapped_column(JSON, nullable=True)
    spotify_url: Mapped[str] = mapped_column(String, nullable=False)
    genres: Mapped[list[str]] = mapped_column(JSON, nullable=True)
    followers: Mapped[int] = mapped_column(Integer, nullable=False)
    popularity: Mapped[int] = mapped_column(Integer, nullable=False)

    # relationship to TopArtist
    top_artists: Mapped[list["TopArtist"]] = relationship(
        back_populates="artist", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Artist(name={self.name}, followers={self.followers})>"


class TopArtist(Base):
    __tablename__ = "top_artist"

    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), primary_key=True, nullable=False)
    artist_id: Mapped[str] = mapped_column(String, ForeignKey("artists.id"), primary_key=True, nullable=False)
    time_range: Mapped[TimeRange] = mapped_column(Enum, nullable=False)
    collection_date: Mapped[date] = mapped_column(Date, nullable=False)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    position_change: Mapped[str | None] = mapped_column(String, nullable=True)

    # relationship to Artist
    artist: Mapped[Artist] = relationship(back_populates="top_artists")

    def __repr__(self) -> str:
        return f"<TopArtist(user_id={self.user_id}, artist_id={self.artist_id}, position={self.position})>"
