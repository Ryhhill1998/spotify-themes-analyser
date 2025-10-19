from datetime import datetime, date, timezone

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import (
    Enum,
    String,
    DateTime,
    Table,
    ForeignKey,
    UniqueConstraint,
    Column,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.models.enums import PositionChange, TimeRange


# -----------------------------
# Base
# -----------------------------
class Base(DeclarativeBase):
    pass


# -----------------------------
# Association tables
# -----------------------------
track_artist_association = Table(
    "track_artist",
    Base.metadata,
    Column("track_id", String, ForeignKey("track.id"), primary_key=True),
    Column("artist_id", String, ForeignKey("artist.id"), primary_key=True),
)


# -----------------------------
# Profile
# -----------------------------
class ProfileDB(Base):
    __tablename__ = "profile"

    id: Mapped[str] = mapped_column(primary_key=True)
    display_name: Mapped[str]
    email: Mapped[str | None]
    images: Mapped[list[dict]] = mapped_column(JSONB)  # list of {height, width, url}
    spotify_url: Mapped[str]
    creation_timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc)
    )
    followers: Mapped[int]


# -----------------------------
# Artist
# -----------------------------
class ArtistDB(Base):
    __tablename__ = "artist"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    images: Mapped[list[dict]] = mapped_column(JSONB)  # list of {height, width, url}
    spotify_url: Mapped[str]
    genres: Mapped[list[str]] = mapped_column(JSONB)
    followers: Mapped[int]
    popularity: Mapped[int]

    tracks: Mapped[list["TrackDB"]] = relationship(
        secondary=track_artist_association, back_populates="artists"
    )


# -----------------------------
# Track
# -----------------------------
class TrackDB(Base):
    __tablename__ = "track"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    images: Mapped[list[dict]] = mapped_column(JSONB)  # list of {height, width, url}
    spotify_url: Mapped[str]
    album_name: Mapped[str]
    release_date: Mapped[str]
    explicit: Mapped[bool]
    duration_ms: Mapped[int]
    popularity: Mapped[int]

    artists: Mapped[list[ArtistDB]] = relationship(
        secondary=track_artist_association, back_populates="tracks"
    )
    lyrics: Mapped["TrackLyricsDB"] = relationship()


# -----------------------------
# Abstract "TopItem" base
# -----------------------------
class TopItemDBBase(Base):
    __abstract__ = True  # prevents a table being created

    user_id: Mapped[str] = mapped_column(ForeignKey("profile.id"), primary_key=True)
    collection_date: Mapped[date] = mapped_column(primary_key=True)
    time_range: Mapped[TimeRange] = mapped_column(
        Enum(TimeRange, name="time_range_enum"), primary_key=True
    )
    position: Mapped[int]
    position_change: Mapped[PositionChange | None] = mapped_column(
        Enum(PositionChange, name="position_change_enum")
    )


# -----------------------------
# TopArtist
# -----------------------------
class TopArtistDB(TopItemDBBase):
    __tablename__ = "top_artist"

    artist_id: Mapped[str] = mapped_column(ForeignKey("artist.id"), primary_key=True)

    artist: Mapped[ArtistDB] = relationship()


# -----------------------------
# TopTrack
# -----------------------------
class TopTrackDB(TopItemDBBase):
    __tablename__ = "top_track"

    track_id: Mapped[str] = mapped_column(ForeignKey("track.id"), primary_key=True)

    track: Mapped[TrackDB] = relationship()

    __table_args__ = (
        UniqueConstraint("user_id", "track_id", "collection_date", "time_range"),
    )


# -----------------------------
# TopGenre
# -----------------------------
class TopGenreDB(TopItemDBBase):
    __tablename__ = "top_genre"

    genre_id: Mapped[str] = mapped_column(primary_key=True)
    percentage: Mapped[float]

    __table_args__ = (
        UniqueConstraint("user_id", "genre_id", "collection_date", "time_range"),
    )


# -----------------------------
# TopEmotion
# -----------------------------
class TopEmotionDB(TopItemDBBase):
    __tablename__ = "top_emotion"

    emotion_id: Mapped[str] = mapped_column(primary_key=True)
    percentage: Mapped[float]

    __table_args__ = (
        UniqueConstraint("user_id", "emotion_id", "collection_date", "time_range"),
    )


# -----------------------------
# TrackLyrics
# -----------------------------
class TrackLyricsDB(Base):
    __tablename__ = "track_lyrics"

    track_id: Mapped[str] = mapped_column(ForeignKey("track.id"), primary_key=True)
    lyrics: Mapped[str]


# -----------------------------
# TrackEmotionalProfile
# -----------------------------
class TrackEmotionalProfileDB(Base):
    __tablename__ = "track_emotional_profile"

    track_id: Mapped[str] = mapped_column(ForeignKey("track.id"), primary_key=True)

    joy: Mapped[float]
    sadness: Mapped[float]
    anger: Mapped[float]
    fear: Mapped[float]
    love: Mapped[float]
    hope: Mapped[float]
    nostalgia: Mapped[float]
    loneliness: Mapped[float]
    confidence: Mapped[float]
    despair: Mapped[float]
    excitement: Mapped[float]
    mystery: Mapped[float]
    defiance: Mapped[float]
    gratitude: Mapped[float]
    spirituality: Mapped[float]
