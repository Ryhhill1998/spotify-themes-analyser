from sqlalchemy.orm import Session
from src.mappers.db_to_dto import top_artist_db_to_top_artist
from src.models.enums import TimeRange
from src.repositories.top_items.base import TopItemsBaseRepository
from src.models.db import TopArtistDB
from src.models.dto import TopArtist
from src.mappers.dto_to_db import top_artist_to_top_artist_db

class TopArtistsRepository(TopItemsBaseRepository):
    def __init__(self, session: Session):
        self.session = session

    def add_many(self, top_artists: list[TopArtist]) -> None:
        db_top_artists = [top_artist_to_top_artist_db(top_artist) for top_artist in top_artists]
        self.session.add_all(db_top_artists)
        self.session.commit()

    def get_previous_top_artists(self, user_id: str, time_range: TimeRange) -> list[TopArtist]:
        db_items = self._get_latest_snapshot(db_model=TopArtistDB, user_id=user_id, time_range=time_range)
        return [top_artist_db_to_top_artist(item) for item in db_items]
