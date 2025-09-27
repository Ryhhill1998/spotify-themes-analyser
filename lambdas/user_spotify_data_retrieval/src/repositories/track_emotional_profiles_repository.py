from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
import sqlalchemy.exc

from src.models.db import TrackEmotionalProfileDB
from src.models.domain import TrackEmotionalProfile


class TrackEmotionalProfilesRepositoryException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class TrackEmotionalProfilesRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def add_many(self, top_items: list[TrackEmotionalProfile]) -> None:
        try:
            values = [
                {"track_id": item.track_id, **item.emotional_profile.model_dump()}
                for item in top_items
            ]
            stmt = insert(TrackEmotionalProfileDB).values(values)
            self.db_session.execute(stmt)
        except sqlalchemy.exc.IntegrityError as e:
            raise TrackEmotionalProfilesRepositoryException(
                "Cannot overwrite an existing emotional profile entry."
            ) from e

    def get_many(self, track_ids: set[str]) -> list[TrackEmotionalProfile]:
        db_track_emotional_profiles = (
            self.db_session.query(TrackEmotionalProfileDB)
            .filter(TrackEmotionalProfileDB.track_id.in_(track_ids))
            .all()
        )
        return [
            TrackEmotionalProfile(track_id=profile.track_id)
            for profile in db_track_emotional_profiles
        ]
