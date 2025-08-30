from dataclasses import asdict
from sqlalchemy.orm import Session
from src.models.domain import TopTrack
from src.models.enums import TimeRange
from src.repositories.top_items.base import TopItemsBaseRepository
from src.models.db import TopTrackDB
from sqlalchemy.dialects.postgresql import insert


class TopTracksRepository(TopItemsBaseRepository):
    def __init__(self, session: Session):
        self.session = session

    def add_many(self, top_tracks: list[TopTrack]) -> None:
        values = [asdict(track) for track in top_tracks]

        stmt = insert(TopTrackDB).values(values)

        self.session.execute(stmt)

        self.session.commit()

    def get_previous_top_tracks(self, user_id: str, time_range: TimeRange) -> list[TopTrack]:
        db_top_tracks = self._get_latest_snapshot(db_model=TopTrackDB, user_id=user_id, time_range=time_range)
        top_tracks = [
            TopTrack(
                user_id=top_track.user_id,
                track_id=top_track.track_id,
                collection_date=top_track.collection_date,
                time_range=top_track.time_range, 
                position=top_track.position,
            ) 
            for top_track in db_top_tracks
        ]
        return top_tracks
