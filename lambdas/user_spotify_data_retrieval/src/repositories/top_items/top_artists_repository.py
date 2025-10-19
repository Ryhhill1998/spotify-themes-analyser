import sqlalchemy
from sqlalchemy.orm import Session
from src.models.domain import TopArtist
from src.repositories.top_items.base import TopItemsBaseRepository
from src.models.db import TopArtistDB


class TopArtistsRepositoryException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class TopArtistsRepository(TopItemsBaseRepository):
    def __init__(self, db_session: Session):
        super().__init__(db_session=db_session, db_model=TopArtistDB)

    def add_many(self, top_items):
        try:
            super().add_many(top_items)
        except sqlalchemy.exc.IntegrityError as e:
            raise TopArtistsRepositoryException(
                "Cannot overwrite a top artist entry."
            ) from e

    @staticmethod
    def _to_domain_objects(db_items: list[TopArtistDB]) -> list[TopArtist]:
        return [
            TopArtist(
                user_id=artist.user_id,
                artist_id=artist.artist_id,
                collection_date=artist.collection_date,
                time_range=artist.time_range,
                position=artist.position,
            )
            for artist in db_items
        ]
