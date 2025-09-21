from typing import AsyncGenerator, Generator
import httpx
import pytest
import pytest_asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from loguru import logger

from src.services.spotify_service import SpotifyService
from src.models.db import Base, ProfileDB

connection_string = "postgresql://neondb_owner:npg_XV9fA5MKUGlD@ep-rapid-cell-abkxf854-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(connection_string)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=True)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture
def existing_profile(db_session) -> ProfileDB:
    existing_profile = ProfileDB(
        id="123",
        display_name="Old First",
        email="old.first.last@domain.com",
        images=[
            {"url": "https://i.scdn.co/image/456", "height": 300, "width": 300},
            {"url": "https://i.scdn.co/image/789", "height": 64, "width": 64},
        ],
        spotify_url="https://open.spotify.com/user/123",
        followers=10,
    )
    db_session.add(existing_profile)
    db_session.commit()
    return existing_profile


@pytest.fixture
def caplog(
    caplog: pytest.LogCaptureFixture,
) -> Generator[pytest.LogCaptureFixture, None, None]:
    handler_id = logger.add(
        caplog.handler,
        format="{message}",
        level=0,
        filter=lambda record: record["level"].no >= caplog.handler.level,
        enqueue=False,  # Set to 'True' if your test is spawning child processes.
    )
    yield caplog
    logger.remove(handler_id)


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[httpx.AsyncClient, None]:
    cl = httpx.AsyncClient()
    yield cl
    await cl.aclose()


@pytest.fixture
def spotify_service(client: httpx.AsyncClient) -> SpotifyService:
    return SpotifyService(client=client, base_url="http://localhost:8000")
