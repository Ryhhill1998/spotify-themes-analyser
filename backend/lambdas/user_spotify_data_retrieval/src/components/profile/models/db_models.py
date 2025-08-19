from datetime import date
from src.shared.models.db import TopItemDBMixin
from src.components.top_artists.models.domain import TopArtist
from src.shared.spotify.enums import TimeRange
from sqlalchemy import ForeignKey, String, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.shared.db import Base


class ProfileDB(Base):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    href: Mapped[str] = mapped_column(String, nullable=True)
    images: Mapped[list[dict[str, int | str]]] = mapped_column(JSON, nullable=True)
    followers: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<User(name={self.name}, email={self.email})>"
