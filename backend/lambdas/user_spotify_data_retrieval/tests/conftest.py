from typing import Generator
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger
from _pytest.logging import LogCaptureFixture

connection_string = "postgresql://neondb_owner:npg_XV9fA5MKUGlD@ep-rapid-cell-abkxf854-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

engine = create_engine(connection_string)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def caplog(caplog: LogCaptureFixture):
    handler_id = logger.add(
        caplog.handler,
        format="{message}",
        level=0,
        filter=lambda record: record["level"].no >= caplog.handler.level,
        enqueue=False,  # Set to 'True' if your test is spawning child processes.
    )
    yield caplog
    logger.remove(handler_id)
