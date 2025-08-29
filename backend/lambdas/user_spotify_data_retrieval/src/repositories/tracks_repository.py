from sqlalchemy.orm import Session
from src.models.db import TrackDB, track_artist_association
from sqlalchemy.dialects.postgresql import insert


class TracksRepository:
    def __init__(self, db_session: Session):
        self.session = db_session

    def upsert_many(self, tracks: list[TrackDB]) -> None:
        # upsert tracks
        values = [
            {
                "id": track.id,
                "name": track.name,
                "spotify_url": track.spotify_url,
                "release_date": track.release_date,
                "explicit": track.explicit,
                "duration_ms": track.duration_ms,
                "popularity": track.popularity,
            }
            for track in tracks
        ]
        
        stmt = insert(TrackDB).values(values)
        stmt = stmt.on_conflict_do_update(
            index_elements=["id"],
            set_={
                "name": stmt.excluded.name,
                "spotify_url": stmt.excluded.spotify_url,
                "release_date": stmt.excluded.release_date,
                "explicit": stmt.excluded.explicit,
                "duration_ms": stmt.excluded.duration_ms,
                "popularity": stmt.excluded.popularity,
            },
        )
        self.session.execute(stmt)

        # upsert track artist association
        association_values = [
            {"track_id": track.id, "artist_id": artist.id}
            for track in tracks
            for artist in track.artists
        ]

        if association_values:
            assoc_stmt = insert(track_artist_association).values(association_values)
            assoc_stmt = assoc_stmt.on_conflict_do_nothing(
                index_elements=["track_id", "artist_id"]
            )
            self.session.execute(assoc_stmt)

        self.session.commit()
