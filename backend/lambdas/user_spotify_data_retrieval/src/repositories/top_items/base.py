from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models.db import TopItemDBBase
from src.models.enums import TimeRange


class TopItemsBaseRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def _get_latest_snapshot(self, db_model: type[TopItemDBBase], user_id: str, time_range: TimeRange) -> list[TopItemDBBase]:
        latest_date = (
            self.db_session
            .query(func.max(db_model.collection_date))
            .filter_by(user_id=user_id, time_range=time_range)
            .scalar()
        )

        if latest_date is None:
            return []

        return (
            self.db_session
            .query(db_model)
            .filter_by(user_id=user_id, time_range=time_range, collection_date=latest_date)
            .all()
        )
