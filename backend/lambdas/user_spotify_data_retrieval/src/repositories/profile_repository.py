from sqlalchemy.orm import Session
from src.models.db import ProfileDB
from loguru import logger


class ProfileRepository:
    def __init__(self, db_session: Session):
        self.session = db_session

    def upsert(self, profile: ProfileDB) -> None:
        """
        Update if exists, else insert new Profile record
        """
        
        profile_id = profile.id
        existing_profile = self.session.get(ProfileDB, profile_id)

        if existing_profile:
            logger.debug(f"Updating existing profile with id: {profile_id}")
            existing_profile.display_name = profile.display_name
            existing_profile.email = profile.email
            existing_profile.images = profile.images
            existing_profile.spotify_url = profile.spotify_url
            existing_profile.followers = profile.followers
        else:
            logger.debug(f"Inserting new profile with id: {profile_id}")
            self.session.add(profile)

        self.session.commit()
