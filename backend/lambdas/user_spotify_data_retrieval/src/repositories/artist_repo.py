from sqlalchemy.orm import Session
from src.mappers.db_to_dto import artist_db_to_artist
from src.mappers.dto_to_db import artist_to_artist_db
from src.models.db import ArtistDB
from src.models.dto import Artist


class ArtistRepository:
    def __init__(self, db_session: Session):
        self.session = db_session

    def get_many(self, artist_ids: list[str]) -> list[Artist]:
        db_artists = (
            self.session.query(ArtistDB).filter(ArtistDB.id.in_(artist_ids)).all()
        )
        artists = [artist_db_to_artist(db_artist) for db_artist in db_artists]

        return artists

    def upsert_many(self, artists: list[Artist]) -> None:
        for artist in artists:
            db_artist = self.session.get(ArtistDB, artist.id)

            if db_artist:
                db_artist.name = artist.name
                db_artist.images = artist.images
                db_artist.spotify_url = artist.spotify_url
                db_artist.genres = artist.genres
                db_artist.followers = artist.followers
                db_artist.popularity = artist.popularity
            else:
                db_artist = artist_to_artist_db(artist)
                self.session.add(db_artist)

        self.session.commit()
