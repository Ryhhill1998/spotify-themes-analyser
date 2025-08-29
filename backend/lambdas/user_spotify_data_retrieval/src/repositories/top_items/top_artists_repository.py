from sqlalchemy.orm import Session
from src.models.enums import TimeRange
from src.repositories.top_items.base import TopItemsBaseRepository
from src.models.db import TopArtistDB
from sqlalchemy.dialects.postgresql import insert


class TopArtistsRepository(TopItemsBaseRepository):
    def __init__(self, session: Session):
        self.session = session

    def add_many(self, top_artists: list[TopArtistDB]) -> None:
        # 1. Convert ORM objects to a list of dictionaries
        values = [
            {
                "id": artist.id,
                "name": artist.name,
                "images": artist.images,
                "spotify_url": artist.spotify_url,
                "genres": artist.genres,
                "followers": artist.followers,
                "popularity": artist.popularity,
            }
            for artist in top_artists
        ]

        # 2. Build the single bulk INSERT statement
        stmt = insert(TopArtistDB).values(values)

        # 3. Execute the statement
        self.session.execute(stmt)

        # 4. Commit the transaction once
        self.session.commit()

    def get_previous_top_artists(self, user_id: str, time_range: TimeRange) -> list[TopArtistDB]:
        previous_top_artists = self._get_latest_snapshot(db_model=TopArtistDB, user_id=user_id, time_range=time_range)
        return previous_top_artists
