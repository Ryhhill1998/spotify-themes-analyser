from sqlalchemy.orm import Session

from backend.lambdas.user_spotify_data_retrieval.src.models.db import TopEmotionDB
from backend.lambdas.user_spotify_data_retrieval.src.models.domain import TopEmotion
from backend.lambdas.user_spotify_data_retrieval.src.repositories.top_items.base import TopItemsBaseRepository


class TopEmotionsRepository(TopItemsBaseRepository[TopEmotionDB, TopEmotion]):
    def __init__(self, db_session: Session):
        super().__init__(db_session=db_session, db_model=TopEmotionDB)

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
