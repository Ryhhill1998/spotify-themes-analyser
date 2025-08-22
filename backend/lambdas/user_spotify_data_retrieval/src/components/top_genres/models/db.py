from datetime import date
from src.shared.models.db import TopItemDBMixin
from src.components.top_genres.models.domain import TopGenre
from src.shared.spotify.enums import TimeRange
from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column

from backend.shared.db import Base


class TopGenreDB(TopItemDBMixin, Base):
    __tablename__ = "top_genre"

    genre_id: Mapped[str] = mapped_column(String, primary_key=True)
    percentage: Mapped[float] = mapped_column(Float, nullable=False)

    @property
    def item_id(self) -> str:
        return self.genre_id
    
    @classmethod
    def from_top_genre(cls, user_id: str, top_genre: TopGenre, time_range: TimeRange, collection_date: date) -> "TopGenreDB":
        return cls(
            user_id=user_id,
            genre_id=top_genre.id,
            time_range=time_range,
            collection_date=collection_date,
            position=top_genre.position,
            position_change=top_genre.position_change,
        )
