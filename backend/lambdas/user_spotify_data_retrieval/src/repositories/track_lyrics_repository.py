from dataclasses import asdict
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from src.models.db import TrackLyricsDB
from src.models.domain import TrackLyrics


class TrackLyricsRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def add_many(self, top_items: list[TrackLyrics]) -> None:
        values = [item.model_dump() for item in top_items]
        stmt = insert(TrackLyricsDB).values(values)
        self.db_session.execute(stmt)
        self.db_session.commit()

    def get_many(self, track_ids: set[str]) -> list[TrackLyrics]:
        db_track_emotional_profiles = (
            self.db_session.query(TrackLyricsDB)
            .filter(TrackLyricsDB.track_id.in_(track_ids))
            .all()
        )
        return [
            TrackLyrics(track_id=profile.track_id)
            for profile in db_track_emotional_profiles
        ]
