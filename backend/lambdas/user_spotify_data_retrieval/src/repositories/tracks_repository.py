from sqlalchemy.orm import Session
from src.mappers.db_to_dto import track_db_to_track
from src.mappers.dto_to_db import track_to_track_db
from src.models.db import TrackDB
from src.models.dto import Track


class TracksRepository:
    def __init__(self, db_session: Session):
        self.session = db_session

    def get_many(self, track_ids: list[str]) -> list[Track]:
        """
        Retrieve tracks by their IDs.
        """
        db_tracks = (
            self.session.query(TrackDB)
            .filter(TrackDB.id.in_(track_ids))
            .all()
        )
        return [track_db_to_track(db_track) for db_track in db_tracks]

    def upsert_many(self, tracks: list[Track]) -> None:
        """
        Insert or update multiple Track objects.
        """
        for track in tracks:
            db_track = self.session.get(TrackDB, track.id)

            if db_track:
                db_track.name = track.name
                db_track.images = track.images
                db_track.spotify_url = track.spotify_url
                db_track.release_date = track.release_date
                db_track.explicit = track.explicit
                db_track.duration_ms = track.duration_ms
                db_track.popularity = track.popularity

                # Replace artists only if necessary
                if track.artists:
                    # db_track.artists should contain ArtistDB objects
                    db_track.artists = [
                        self.session.get(ArtistDB, a.id) for a in track.artists
                    ]
            else:
                db_track = track_to_track_db(track)
                self.session.add(db_track)

        self.session.commit()
