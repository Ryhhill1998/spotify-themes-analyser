import sqlalchemy
from sqlalchemy.orm import Session
from src.models.domain import TopGenre
from src.repositories.top_items.base import TopItemsBaseRepository
from src.models.db import TopGenreDB


class TopGenresRepositoryException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class TopGenresRepository(TopItemsBaseRepository):
    def __init__(self, db_session: Session):
        super().__init__(db_session=db_session, db_model=TopGenreDB)

    def add_many(self, top_items: list[TopGenre]) -> None:
        try:
            super().add_many(top_items)
        except sqlalchemy.exc.IntegrityError as e:
            raise TopGenresRepositoryException(
                "Cannot overwrite a top genre entry."
            ) from e

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
