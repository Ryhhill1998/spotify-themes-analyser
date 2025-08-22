from datetime import date
from src.shared.models.domain import TopItem
from src.components.top_tracks.models.domain import TopTrack
from src.shared.base_respository import BaseRepository
from src.components.top_tracks.models.db import TrackDB, TopTrackDB
from src.shared.spotify.enums import TimeRange
from sqlalchemy.orm import Session


class TopTracksRepository(BaseRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_previous_top_tracks(self, user_id: str, time_range: TimeRange) -> list[TopItem]:
        return self.get_previous_top_items(db_model=TopTrackDB, user_id=user_id, time_range=time_range)

    def store_top_tracks(self, user_id: str, top_tracks: list[TopTrack], time_range: TimeRange, collection_date: date) -> None:
        # store tracks in the database
        db_tracks = [TrackDB.from_top_track(track) for track in top_tracks]
        self.db_session.add_all(db_tracks)

        # store top tracks in the database
        db_top_tracks = [
            TopTrackDB.from_top_track(user_id, track, time_range, collection_date) for track in top_tracks
        ]
        self.db_session.add_all(db_top_tracks)
        self.db_session.commit()
