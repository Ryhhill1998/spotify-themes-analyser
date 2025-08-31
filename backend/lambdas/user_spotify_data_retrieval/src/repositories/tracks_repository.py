from dataclasses import asdict
from sqlalchemy.orm import Session
from src.models.domain import Track
from src.models.db import TrackDB, track_artist_association
from sqlalchemy.dialects.postgresql import insert


class TracksRepository:
    def __init__(self, db_session: Session):
        self.session = db_session

    def upsert_many(self, tracks: list[Track]) -> None:
        # upsert tracks
        values = []
        
        for track in tracks:
            track_data = asdict(track)
            track_data.pop("artist_ids")
            values.append(track_data)
        
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
            {"track_id": track.id, "artist_id": artist_id}
            for track in tracks
            for artist_id in track.artist_ids
        ]

        if association_values:
            assoc_stmt = insert(track_artist_association).values(association_values)
            assoc_stmt = assoc_stmt.on_conflict_do_nothing(
                index_elements=["track_id", "artist_id"]
            )
            self.session.execute(assoc_stmt)

        self.session.commit()
