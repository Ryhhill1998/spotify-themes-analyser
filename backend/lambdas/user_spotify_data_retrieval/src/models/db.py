from datetime import datetime, date

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Enum, String, DateTime, Table, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.models.enums import TimeRange


# -----------------------------
# Base
# -----------------------------
class Base(DeclarativeBase):
    pass


# -----------------------------
# Abstract "TopItem" base
# -----------------------------
class TopItemBase(Base):
    __abstract__ = True  # prevents a table being created

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("profile.id"))
    collection_date: Mapped[date]
    time_range: Mapped[TimeRange] = mapped_column(Enum(TimeRange, name="time_range_enum"))
    position: Mapped[int]
    position_change: Mapped[int | None]


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

    id: Mapped[str] = mapped_column(primary_key=True)
    display_name: Mapped[str]
    email: Mapped[str | None]
    images: Mapped[list[dict]] = mapped_column(JSONB) # list of {height, width, url}
    spotify_url: Mapped[str]
    creation_timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(datetime.timezone.utc))
    followers: Mapped[int]


# -----------------------------
# Artist
# -----------------------------
class Artist(Base):
    __tablename__ = "artist"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    images: Mapped[list[dict]] = mapped_column(JSONB)  # list of {height, width, url}
    spotify_url: Mapped[str]
    genres: Mapped[list[str]] = mapped_column(JSONB)
    followers: Mapped[int]
    popularity: Mapped[int]

    tracks: Mapped[list["Track"]] = relationship(secondary=track_artist_table, back_populates="artists")


# -----------------------------
# Track
# -----------------------------
class Track(Base):
    __tablename__ = "track"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    images: Mapped[list[dict]] = mapped_column(JSONB)  # list of {height, width, url}
    spotify_url: Mapped[str]
    release_date: Mapped[datetime]
    explicit: Mapped[bool]
    duration_ms: Mapped[int]
    popularity: Mapped[int]

    artists: Mapped[list[Artist]] = relationship(secondary=track_artist_table, back_populates="tracks")


# -----------------------------
# TopArtist
# -----------------------------
class TopArtist(TopItemBase):
    __tablename__ = "top_artist"

    artist_id: Mapped[str] = mapped_column(ForeignKey("artist.id"))

    artist: Mapped[Artist] = relationship()

    __table_args__ = (
        UniqueConstraint("user_id", "artist_id", "collection_date", "time_range"),
    )


# -----------------------------
# TopTrack
# -----------------------------
class TopTrack(TopItemBase):
    __tablename__ = "top_track"

    track_id: Mapped[str] = mapped_column(ForeignKey("track.id"))

    track: Mapped[Track] = relationship()

    __table_args__ = (
        UniqueConstraint("user_id", "track_id", "collection_date", "time_range"),
    )


# -----------------------------
# TopGenre
# -----------------------------
class TopGenre(TopItemBase):
    __tablename__ = "top_genre"

    genre_id: Mapped[str]
    percentage: Mapped[float]

    __table_args__ = (
        UniqueConstraint("user_id", "genre_id", "collection_date", "time_range"),
    )


# -----------------------------
# TopEmotion
# -----------------------------
class TopEmotion(TopItemBase):
    __tablename__ = "top_emotion"

    emotion_id: Mapped[str]
    percentage: Mapped[float]

    __table_args__ = (
        UniqueConstraint("user_id", "emotion_id", "collection_date", "time_range"),
    )
