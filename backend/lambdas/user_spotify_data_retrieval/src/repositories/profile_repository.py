from sqlalchemy.orm import Session
from src.mappers.dto_to_db import profile_to_profile_db
from src.models.db import ProfileDB
from src.models.dto import Profile
from loguru import logger


class ProfileRepository:
    def __init__(self, db_session: Session):
        self.session = db_session

    def upsert(self, profile: Profile) -> None:
        """
        Update if exists, else insert new Profile record
        """
        
        db_profile = self.session.get(ProfileDB, profile.id)

        if db_profile:
            logger.debug(f"Updating existing profile with id: {db_profile.id}")
            db_profile.display_name = profile.display_name
            db_profile.email = profile.email
            db_profile.images = profile.images
            db_profile.spotify_url = profile.spotify_url
            db_profile.followers = profile.followers
        else:
            db_profile = profile_to_profile_db(profile)
            logger.debug(f"Inserting new profile with id: {db_profile.id}")
            self.session.add(db_profile)

        self.session.commit()
