from datetime import date
from src.shared.models.domain import TopItem
from src.components.top_genres.models.domain import TopGenre
from src.shared.base_respository import BaseRepository
from src.components.top_genres.models.db import TopGenreDB
from src.shared.spotify.enums import TimeRange
from sqlalchemy.orm import Session


class TopGenresRepository(BaseRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_previous_top_genres(self, user_id: str, time_range: TimeRange) -> list[TopItem]:
        return self.get_previous_top_items(db_model=TopGenreDB, user_id=user_id, time_range=time_range)

    def store_top_genres(self, user_id: str, top_genres: list[TopGenre], time_range: TimeRange, collection_date: date) -> None:
        # store top genres in the database
        db_top_genres = [
            TopGenreDB.from_top_genre(user_id, genre, time_range, collection_date) for genre in top_genres
        ]
        self.db_session.add_all(db_top_genres)
        self.db_session.commit()
