from datetime import date
from src.components.top_artists.models.domain import PreviousTopArtist, TopArtist
from src.components.top_artists.models.db import ArtistDB, TopArtistDB
from src.shared.spotify.enums import TimeRange
from sqlalchemy.orm import Session
from sqlalchemy import func


class TopArtistsRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def get_previous_top_artists(self, user_id: str, time_range: TimeRange) -> list[PreviousTopArtist]:
        # 1. Find the latest collection_date
        latest_date = (
            self.db_session
            .query(func.max(TopArtistDB.collection_date))
            .filter_by(user_id=user_id, time_range=time_range)
            .scalar()
        )

        if latest_date is None:
            return []

        # 2. Retrieve all top artists for that date
        top_artists_db = (
            self.db_session
            .query(TopArtistDB)
            .filter_by(user_id=user_id, time_range=time_range, collection_date=latest_date)
            .all()
        )

        # 3. Convert to domain model
        previous_top_artists = [
            PreviousTopArtist.from_top_artist_db(top_artist)
            for top_artist in top_artists_db
        ]

        return previous_top_artists

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
