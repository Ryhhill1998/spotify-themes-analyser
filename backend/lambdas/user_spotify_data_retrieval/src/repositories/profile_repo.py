from sqlalchemy.orm import Session
from src.models.db import ProfileDB
from src.models.dto import Profile


class ProfileRepo:
    def __init__(self, db_session: Session):
        self.session = db_session

    def upsert(self, profile: Profile) -> None:
        """
        Update if exists, else insert new Profile record
        """
        
        db_obj = self.session.get(ProfileDB, profile.id)

        if db_obj:
            # Update fields
            db_obj.display_name = profile.display_name
            db_obj.email = profile.email
            db_obj.images = profile.images
            db_obj.spotify_url = profile.spotify_url
            db_obj.followers = profile.followers
        else:
            # Insert new
            db_obj = ProfileDB(
                id=profile.id,
                name=profile.display_name,
                email=profile.email,
                image_url=profile.images,
                spotify_url=profile.spotify_url,
                followers=profile.followers,
            )
            self.session.add(db_obj)

        self.session.commit()
