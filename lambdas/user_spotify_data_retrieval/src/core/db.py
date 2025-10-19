from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger

from src.models.db import Base


def create_session_factory(connection_string: str):
    engine = create_engine(connection_string)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autocommit=False, autoflush=True)


@contextmanager
def get_db_session(connection_string: str) -> Generator[Session, None, None]:
    SessionLocal = create_session_factory(connection_string)
    session = SessionLocal()

    try:
        yield session
        session.commit()
    except Exception:
        logger.exception("Transaction failed, rolling back")
        session.rollback()
    finally:
        session.close()
