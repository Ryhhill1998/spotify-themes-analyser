from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from src.models.domain import TopItemBase
from src.models.db import TopItemDBBase
from src.models.enums import TimeRange

TopItemDBType = TypeVar("TopItemDBType", bound=TopItemDBBase)
TopItemDomainType = TypeVar("TopItemDomainType", bound=TopItemBase)


class TopItemsBaseRepository(ABC, Generic[TopItemDBType, TopItemDomainType]):
    def __init__(self, db_session: Session, db_model: TopItemDBType):
        self.db_session = db_session
        self.db_model = db_model

    def add_many(self, top_items: list[TopItemDomainType]) -> None:
        values = [item.model_dump() for item in top_items]
        stmt = insert(self.db_model).values(values)
        self.db_session.execute(stmt)

    def _get_latest_snapshot(
        self,
        user_id: str,
        time_range: TimeRange,
    ) -> list[TopItemDBType]:
        latest_date_subquery = (
            self.db_session
            .query(func.max(self.db_model.collection_date))
            .filter(
                self.db_model.user_id == user_id,
                self.db_model.time_range == time_range
            )
            .scalar_subquery()
        )

        return (
            self.db_session
            .query(self.db_model)
            .filter(
                self.db_model.user_id == user_id,
                self.db_model.time_range == time_range,
                self.db_model.collection_date == latest_date_subquery
            )
            .all()
        )
    
    @staticmethod
    @abstractmethod
    def _to_domain_objects(db_items: list[TopItemDBType]) -> list[TopItemDomainType]: ...
    
    def get_previous_top_items(self, user_id: str, time_range: TimeRange) -> TopItemDomainType:
        db_top_items = self._get_latest_snapshot(user_id=user_id, time_range=time_range) 
        return self._to_domain_objects(db_top_items)
