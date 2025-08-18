from datetime import date
from src.shared.spotify.enums import TimeRange
from sqlalchemy import String, Integer, Date, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class TopItemDBMixin:
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), primary_key=True)
    item_id: Mapped[str] = mapped_column(String)  # overridden via property in child classes
    time_range: Mapped[TimeRange] = mapped_column(Enum, nullable=False, primary_key=True)
    collection_date: Mapped[date] = mapped_column(Date, nullable=False, primary_key=True)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    position_change: Mapped[str | None] = mapped_column(String, nullable=True)
