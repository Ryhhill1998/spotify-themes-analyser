from src.shared.models.db import TopItemDBMixin
from src.shared.models.domain import TopItem
from src.shared.spotify.enums import TimeRange
from sqlalchemy.orm import Session
from sqlalchemy import func


class BaseRespository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_previous_top_items(
        self, db_model: type[TopItemDBMixin], user_id: str, time_range: TimeRange
    ) -> list[TopItem]:
        # 1. Find the latest collection_date
        latest_date = (
            self.db_session
            .query(func.max(db_model.collection_date))
            .filter_by(user_id=user_id, time_range=time_range)
            .scalar()
        )

        if latest_date is None:
            return []

        # 2. Retrieve all top items for that date
        top_items_db = (
            self.db_session
            .query(db_model)
            .filter_by(user_id=user_id, time_range=time_range, collection_date=latest_date)
            .all()
        )

        # 3. Convert to generic TopItem
        return [TopItem.from_db(item) for item in top_items_db]
