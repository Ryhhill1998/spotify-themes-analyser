from src.components.users.models.db import UserDB
from src.components.users.models.domain import User
from src.shared.base_respository import BaseRepository
from sqlalchemy.orm import Session


class UserRepository(BaseRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def store_user_profile(self, user: User) -> None:
        db_user = UserDB.from_user(user)
        self.db_session.add(db_user)
        self.db_session.commit()
