from sqlalchemy.orm import Session
from src.models.domain import Artist
from src.models.db import ArtistDB
from sqlalchemy.dialects.postgresql import insert


class ArtistsRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def upsert_many(self, artists: list[Artist]) -> None:
        values = [artist.model_dump() for artist in artists]

        stmt = insert(ArtistDB).values(values)
        stmt = stmt.on_conflict_do_update(
            index_elements=["id"],
            set_={
                "name": stmt.excluded.name,
                "images": stmt.excluded.images,
                "spotify_url": stmt.excluded.spotify_url,
                "genres": stmt.excluded.genres,
                "followers": stmt.excluded.followers,
                "popularity": stmt.excluded.popularity,
            },
        )

        self.db_session.execute(stmt)
