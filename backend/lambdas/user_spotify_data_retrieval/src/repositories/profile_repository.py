from sqlalchemy.orm import Session
from src.models.db import ProfileDB
from src.models.dto import Profile


class ProfileRepository:
    def __init__(self, db_session: Session):
        self.session = db_session

    def upsert(self, profile: Profile) -> None:
        """
        Update if exists, else insert new Profile record
        """
        
        db_profile = self.session.get(ProfileDB, profile.id)

        if db_profile:
            db_profile.display_name = profile.display_name
            db_profile.email = profile.email
            db_profile.images = profile.images
            db_profile.spotify_url = profile.spotify_url
            db_profile.followers = profile.followers
        else:
            db_profile = ProfileDB(
                id=profile.id,
                name=profile.display_name,
                email=profile.email,
                image_url=profile.images,
                spotify_url=profile.spotify_url,
                followers=profile.followers,
            )
            self.session.add(db_profile)

        self.session.commit()
