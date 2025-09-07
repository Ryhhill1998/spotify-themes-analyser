from sqlalchemy.orm import Session
from src.models.domain import TopGenre
from src.repositories.top_items.base import TopItemsBaseRepository
from src.models.db import TopGenreDB


class TopGenresRepository(TopItemsBaseRepository):
    def __init__(self, db_session: Session):
        super().__init__(db_session=db_session, db_model=TopGenreDB)

    @staticmethod
    def _to_domain_objects(db_items: list[TopGenreDB]) -> list[TopGenre]:
        return [
            TopGenre(
                user_id=genre.user_id,
                genre_id=genre.genre_id,
                collection_date=genre.collection_date,
                time_range=genre.time_range, 
                position=genre.position,
                percentage=genre.percentage,
            )
            for genre in db_items
        ]
