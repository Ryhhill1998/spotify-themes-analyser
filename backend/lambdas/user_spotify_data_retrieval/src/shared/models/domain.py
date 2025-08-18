from src.shared.models.db import TopItemDBMixin
from pydantic import BaseModel


class TopItem(BaseModel):
    id: str
    position: int | None = None
    position_change: str | None = None

    @classmethod
    def from_db(cls, db_item: TopItemDBMixin) -> "TopItem":
        return cls(
            id=db_item.item_id,
            position=db_item.position,
            position_change=db_item.position_change,
        )
