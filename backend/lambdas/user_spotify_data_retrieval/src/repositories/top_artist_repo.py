from sqlalchemy.orm import Session
from src.models.db import TopArtistDB
from src.models.dto import TopArtist
from src.mappers.dto_to_db import top_artist_to_top_artist_db

class TopArtistsRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_many(self, top_artists: list[TopArtist]) -> None:
        db_top_artists = [top_artist_to_top_artist_db(top_artist) for top_artist in top_artists]
        self.session.add_all(db_top_artists)
        self.session.commit()
