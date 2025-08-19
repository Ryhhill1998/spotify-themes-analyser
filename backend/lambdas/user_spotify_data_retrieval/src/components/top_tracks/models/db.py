from datetime import date
from src.components.top_artists.models.db import ArtistDB
from src.shared.models.db import TopItemDBMixin, track_artist_association_table
from src.components.top_tracks.models.domain import TopTrack
from src.shared.spotify.enums import TimeRange
from sqlalchemy import ForeignKey, String, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.shared.db import Base


class TrackDB(Base):
    __tablename__ = "track"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    images: Mapped[list[dict[str, int | str]]] = mapped_column(JSON, nullable=True)
    spotify_url: Mapped[str] = mapped_column(String, nullable=False)
    release_date: Mapped[str] = mapped_column(String, nullable=True)
    album_name: Mapped[str] = mapped_column(String, nullable=True)
    explicit: Mapped[bool] = mapped_column(Integer, nullable=False)
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    popularity: Mapped[int] = mapped_column(Integer, nullable=False)

    artists: Mapped[list["ArtistDB"]] = relationship(
        "ArtistDB", 
        secondary=track_artist_association_table, 
        back_populates="tracks",
    )
    
    @classmethod
    def from_top_track(cls, top_track: TopTrack) -> "TrackDB":
        return cls(
            id=top_track.id,
            name=top_track.name,
            images=[image.dict() for image in top_track.images],
            spotify_url=top_track.spotify_url,
            artist_id=top_track.artist.id,
            release_date=top_track.release_date,
            album_name=top_track.album_name,
            explicit=top_track.explicit,
            duration_ms=top_track.duration_ms,
            followers=top_track.followers,
            popularity=top_track.popularity,
        )


class TopTrackDB(TopItemDBMixin, Base):
    __tablename__ = "top_track"

    track_id: Mapped[str] = mapped_column(String, ForeignKey("tracks.id", ondelete="CASCADE"), primary_key=True)

    track: Mapped[TrackDB] = relationship()

    @property
    def item_id(self) -> str:
        return self.track_id
    
    @classmethod
    def from_top_track(cls, user_id: str, top_track: TopTrack, time_range: TimeRange, collection_date: date) -> "TopTrackDB":
        return cls(
            user_id=user_id,
            track_id=top_track.id,
            time_range=time_range,
            collection_date=collection_date,
            position=top_track.position,
            position_change=top_track.position_change,
        )
