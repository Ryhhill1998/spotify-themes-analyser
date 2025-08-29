from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models.db import TopItemDBBase
from src.models.enums import TimeRange


class TopItemsBaseRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def _get_latest_snapshot[TopItemType: TopItemDBBase](self, db_model: type[TopItemType], user_id: str, time_range: TimeRange) -> list[TopItemType]:
        latest_date_subquery = (
            self.db_session
            .query(func.max(db_model.collection_date))
            .filter(
                db_model.user_id == user_id,
                db_model.time_range == time_range
            )
            .scalar_subquery()
        )

        return (
            self.db_session
            .query(db_model)
            .filter(
                db_model.user_id == user_id,
                db_model.time_range == time_range,
                db_model.collection_date == latest_date_subquery
            )
            .all()
        )
