from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.models.db import Base


def create_session_factory(connection_string: str):
    engine = create_engine(connection_string)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


@contextmanager
def get_db_session(connection_string: str) -> Generator[Session, None, None]:
    SessionLocal = create_session_factory(connection_string)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
