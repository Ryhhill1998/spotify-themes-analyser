from sqlalchemy.orm import Session
from src.mappers.db_to_dto import top_track_db_to_top_track
from src.mappers.dto_to_db import top_track_to_top_track_db
from src.models.enums import TimeRange
from src.repositories.top_items.base import TopItemsBaseRepository
from src.models.db import TopTrackDB
from src.models.dto import TopTrack


class TopTracksRepository(TopItemsBaseRepository):
    def __init__(self, session: Session):
        self.session = session

    def add_many(self, top_tracks: list[TopTrack]) -> None:
        db_top_tracks = [top_track_to_top_track_db(track) for track in top_tracks]
        self.session.add_all(db_top_tracks)
        self.session.commit()

    def get_previous_top_tracks(self, user_id: str, time_range: TimeRange) -> list[TopTrack]:
        db_items = self._get_latest_snapshot(db_model=TopTrackDB, user_id=user_id, time_range=time_range)
        return [top_track_db_to_top_track(item) for item in db_items]
