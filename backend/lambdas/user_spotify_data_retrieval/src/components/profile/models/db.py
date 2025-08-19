from sqlalchemy import String, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column

from backend.shared.db import Base


class ProfileDB(Base):
    __tablename__ = "profile"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=True)
    href: Mapped[str] = mapped_column(String, nullable=False)
    images: Mapped[list[dict[str, int | str]]] = mapped_column(JSON, nullable=False)
    followers: Mapped[int] = mapped_column(Integer, nullable=False)

    def __repr__(self) -> str:
        return f"<User(display_name={self.display_name}, email={self.email})>"
