from sqlalchemy.orm import Session
from src.mappers.dto_to_db import track_to_track_db
from src.models.db import ArtistDB, TrackDB
from src.models.dto import Track


class TracksRepository:
    def __init__(self, db_session: Session):
        self.session = db_session

    def upsert_many(self, tracks: list[Track]) -> None:
        """
        Insert or update multiple Track objects.
        """

        for track in tracks:
            db_track = self.session.get(TrackDB, track.id)
            track_artists = [self.session.get(ArtistDB, artist.id) for artist in track.artists]

            if db_track:
                db_track.name = track.name
                db_track.images = track.images
                db_track.spotify_url = track.spotify_url
                db_track.release_date = track.release_date
                db_track.explicit = track.explicit
                db_track.duration_ms = track.duration_ms
                db_track.popularity = track.popularity
                db_track.artists = track_artists
            else:
                db_track = track_to_track_db(track=track, db_artists=track_artists)
                self.session.add(db_track)

        self.session.commit()
