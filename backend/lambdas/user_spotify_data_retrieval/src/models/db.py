from datetime import datetime
from typing import List, Dict

from sqlalchemy import String, Integer, Float, Boolean, DateTime, JSON, Table, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# -----------------------------
# Base
# -----------------------------
class Base(DeclarativeBase):
    pass


# -----------------------------
# Association tables
# -----------------------------
track_artist_table = Table(
    "track_artist",
    Base.metadata,
    mapped_column("track_id", String, ForeignKey("track.id"), primary_key=True),
    mapped_column("artist_id", String, ForeignKey("artist.id"), primary_key=True),
)


# -----------------------------
# Profile
# -----------------------------
class Profile(Base):
    __tablename__ = "profile"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String, nullable=True)
    creation_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    followers: Mapped[int] = mapped_column(Integer, default=0)

    top_artists: Mapped[List["TopArtist"]] = relationship(back_populates="profile")
    top_tracks: Mapped[List["TopTrack"]] = relationship(back_populates="profile")
    top_genres: Mapped[List["TopGenre"]] = relationship(back_populates="profile")
    top_emotions: Mapped[List["TopEmotion"]] = relationship(back_populates="profile")


# -----------------------------
# Artist
# -----------------------------
class Artist(Base):
    __tablename__ = "artist"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    images: Mapped[List[Dict]] = mapped_column(JSON)  # List of {height, width, url}
    genres: Mapped[List[str]] = mapped_column(JSON)
    followers: Mapped[int] = mapped_column(Integer, default=0)
    popularity: Mapped[int] = mapped_column(Integer, default=0)
    spotify_url: Mapped[str | None] = mapped_column(String, nullable=True)

    tracks: Mapped[List["Track"]] = relationship(
        secondary=track_artist_table,
        back_populates="artists"
    )


# -----------------------------
# Track
# -----------------------------
class Track(Base):
    __tablename__ = "track"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    images: Mapped[List[Dict]] = mapped_column(JSON)
    spotify_url: Mapped[str | None] = mapped_column(String, nullable=True)
    release_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    explicit: Mapped[bool] = mapped_column(Boolean, default=False)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    popularity: Mapped[int] = mapped_column(Integer, default=0)

    artists: Mapped[List[Artist]] = relationship(
        secondary=track_artist_table,
        back_populates="tracks"
    )


# -----------------------------
# TopArtist
# -----------------------------
class TopArtist(Base):
    __tablename__ = "top_artist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("profile.id"), nullable=False)
    artist_id: Mapped[str] = mapped_column(ForeignKey("artist.id"), nullable=False)
    collection_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    time_range: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    position_change: Mapped[int | None] = mapped_column(Integer, nullable=True)

    artist: Mapped[Artist] = relationship()


# -----------------------------
# TopTrack
# -----------------------------
class TopTrack(Base):
    __tablename__ = "top_track"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("profile.id"), nullable=False)
    track_id: Mapped[str] = mapped_column(ForeignKey("track.id"), nullable=False)
    collection_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    time_range: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    position_change: Mapped[int | None] = mapped_column(Integer, nullable=True)

    track: Mapped[Track] = relationship()


# -----------------------------
# TopGenre
# -----------------------------
class TopGenre(Base):
    __tablename__ = "top_genre"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("profile.id"), nullable=False)
    genre_id: Mapped[str] = mapped_column(String, nullable=False)
    percentage: Mapped[float] = mapped_column(Float, nullable=False)
    collection_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    time_range: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    position_change: Mapped[int | None] = mapped_column(Integer, nullable=True)


# -----------------------------
# TopEmotion
# -----------------------------
class TopEmotion(Base):
    __tablename__ = "top_emotion"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("profile.id"), nullable=False)
    emotion_id: Mapped[str] = mapped_column(String, nullable=False)
    percentage: Mapped[float] = mapped_column(Float, nullable=False)
    collection_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    time_range: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    position_change: Mapped[int | None] = mapped_column(Integer, nullable=True)
