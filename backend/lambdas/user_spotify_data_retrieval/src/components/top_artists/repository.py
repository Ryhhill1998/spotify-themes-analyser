from datetime import date
from src.shared.spotify.enums import TimeRange
from sqlalchemy.orm import Session


class TopArtistsRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_top_artists(self, user_id: str) -> list:
        # Logic to retrieve top artists from the database for the given user_id
        pass

    def store_top_artists(self, user_id: str, artists: list, time_range: TimeRange, collection_date: date) -> None:
        # Logic to store top artists in the database for the given user_id
        pass
