from dataclasses import asdict
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from src.models.db import TrackEmotionalProfileDB
from src.models.domain import TrackEmotionalProfile


class EmotionalProfilesRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def add_many(self, top_items: list[TrackEmotionalProfile]) -> None:
        values = [asdict(item) for item in top_items]
        stmt = insert(self.db_model).values(values)
        self.db_session.execute(stmt)
        self.db_session.commit()

    def get_many(self, track_ids: set[str]) -> list[TrackEmotionalProfile]:
        db_track_emotional_profiles = (
            self.db_session.query(TrackEmotionalProfileDB)
            .filter(TrackEmotionalProfile.track_id.in_(track_ids))
            .all()
        )
        return [
            TrackEmotionalProfile(track_id=profile.track_id)
            for profile in db_track_emotional_profiles
        ]
