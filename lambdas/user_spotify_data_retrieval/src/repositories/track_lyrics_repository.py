from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
import sqlalchemy.exc

from src.models.db import TrackLyricsDB
from src.models.domain import TrackLyrics


class TrackLyricsRepositoryException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class TrackLyricsRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def add_many(self, top_items: list[TrackLyrics]) -> None:
        try:
            values = [item.model_dump() for item in top_items]
            stmt = insert(TrackLyricsDB).values(values)
            self.db_session.execute(stmt)
        except sqlalchemy.exc.IntegrityError as e:
            raise TrackLyricsRepositoryException(
                "Cannot overwrite an existing lyrics entry."
            ) from e

    def get_many(self, track_ids: set[str]) -> list[TrackLyrics]:
        db_track_lyrics = (
            self.db_session.query(TrackLyricsDB)
            .filter(TrackLyricsDB.track_id.in_(track_ids))
            .all()
        )
        return [
            TrackLyrics(track_id=profile.track_id, lyrics=profile.lyrics)
            for profile in db_track_lyrics
        ]
