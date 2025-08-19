from src.components.profile.models.db import ProfileDB
from src.components.profile.models.domain import Profile
from src.shared.base_respository import BaseRepository
from sqlalchemy.orm import Session


class ProfileRepository(BaseRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def store_user_profile(self, profile: Profile) -> None:
        db_profile = ProfileDB.from_profile(profile)
        self.db_session.add(db_profile)
        self.db_session.commit()
