from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from src.models.domain import Profile
from src.models.db import ProfileDB


class ProfileRepository:
    def __init__(self, db_session: Session):
        self.session = db_session

    def upsert(self, profile: Profile) -> None:
        values = {
            "id": profile.id,
            "display_name": profile.name,
            "email": profile.email,
            "images": profile.images,
            "spotify_url": profile.spotify_url,
            "followers": profile.followers,
        }

        stmt = insert(ProfileDB).values(values)
        stmt = stmt.on_conflict_do_update(
            index_elements=["id"],
            set_={
                "display_name": stmt.excluded.display_name,
                "email": stmt.excluded.email,
                "images": stmt.excluded.images,
                "spotify_url": stmt.excluded.spotify_url,
                "followers": stmt.excluded.followers,
            },
        )

        self.session.execute(stmt)
        self.session.commit()
