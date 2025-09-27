import sqlalchemy
from sqlalchemy.orm import Session

from src.models.db import TopEmotionDB
from src.models.domain import TopEmotion
from src.repositories.top_items.base import TopItemsBaseRepository


class TopEmotionsRepositoryException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class TopEmotionsRepository(TopItemsBaseRepository[TopEmotionDB, TopEmotion]):
    def __init__(self, db_session: Session):
        super().__init__(db_session=db_session, db_model=TopEmotionDB)

    def add_many(self, top_items):
        try:
            super().add_many(top_items)
        except sqlalchemy.exc.IntegrityError as e:
            raise TopEmotionsRepositoryException(
                "Cannot overwrite a top emotion entry."
            ) from e

    @staticmethod
    def _to_domain_objects(db_items: list[TopEmotionDB]) -> list[TopEmotion]:
        return [
            TopEmotion(
                user_id=emotion.user_id,
                emotion_id=emotion.emotion_id,
                collection_date=emotion.collection_date,
                time_range=emotion.time_range,
                position=emotion.position,
                percentage=emotion.percentage,
            )
            for emotion in db_items
        ]
