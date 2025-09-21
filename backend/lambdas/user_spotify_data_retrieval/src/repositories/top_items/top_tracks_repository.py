import sqlalchemy
from sqlalchemy.orm import Session
from src.models.domain import TopTrack
from src.repositories.top_items.base import TopItemsBaseRepository
from src.models.db import TopTrackDB


class TopTracksRepositoryException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class TopTracksRepository(TopItemsBaseRepository):
    def __init__(self, db_session: Session):
        super().__init__(db_session=db_session, db_model=TopTrackDB)

    def add_many(self, top_items):
        try:
            super().add_many(top_items)
        except sqlalchemy.exc.IntegrityError as e:
            raise TopTracksRepository("Cannot overwrite a top track entry.") from e

    @staticmethod
    def _to_domain_objects(db_items: list[TopTrackDB]) -> list[TopTrack]:
        return [
            TopTrack(
                user_id=top_track.user_id,
                track_id=top_track.track_id,
                collection_date=top_track.collection_date,
                time_range=top_track.time_range,
                position=top_track.position,
            )
            for top_track in db_items
        ]
