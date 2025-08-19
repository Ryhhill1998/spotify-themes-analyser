from datetime import date
from src.shared.models.domain import TopItem
from src.components.top_artists.models.domain import TopArtist
from src.shared.base_respository import BaseRepository
from src.components.top_artists.models.db import ArtistDB, TopArtistDB
from src.shared.spotify.enums import TimeRange
from sqlalchemy.orm import Session


class TopArtistsRepository(BaseRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_previous_top_artists(self, user_id: str, time_range: TimeRange) -> list[TopItem]:
        return self.get_previous_top_items(db_model=TopArtistDB, user_id=user_id, time_range=time_range)

    def store_top_artists(self, user_id: str, top_artists: list[TopArtist], time_range: TimeRange, collection_date: date) -> None:
        # store artists in the database
        db_artists = [ArtistDB.from_top_artist(artist) for artist in top_artists]
        self.db_session.add_all(db_artists)

        # store top artists in the database
        db_top_artists = [
            TopArtistDB.from_top_artist(user_id, artist, time_range, collection_date) for artist in top_artists
        ]
        self.db_session.add_all(db_top_artists)
        self.db_session.commit()
