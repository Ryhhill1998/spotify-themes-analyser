from dataclasses import asdict
from sqlalchemy.orm import Session
from src.models.domain import TopArtist
from src.models.enums import TimeRange
from src.repositories.top_items.base import TopItemsBaseRepository
from src.models.db import TopArtistDB
from sqlalchemy.dialects.postgresql import insert


class TopArtistsRepository(TopItemsBaseRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def add_many(self, top_artists: list[TopArtist]) -> None:
        # 1. Convert ORM objects to a list of dictionaries
        values = [asdict(artist) for artist in top_artists]

        # 2. Build the single bulk INSERT statement
        stmt = insert(TopArtistDB).values(values)

        # 3. Execute the statement
        self.db_session.execute(stmt)

        # 4. Commit the transaction once
        self.db_session.commit()

    def get_previous_top_artists(self, user_id: str, time_range: TimeRange) -> list[TopArtist]:
        db_top_artists = self._get_latest_snapshot(db_model=TopArtistDB, user_id=user_id, time_range=time_range)
        top_artists = [
            TopArtist(
                user_id=artist.user_id,
                artist_id=artist.artist_id,
                collection_date=artist.collection_date,
                time_range=artist.time_range, 
                position=artist.position,
            )
            for artist in db_top_artists
        ]
        return top_artists
