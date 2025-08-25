import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

connection_string = "postgresql://neondb_owner:npg_XV9fA5MKUGlD@ep-rapid-cell-abkxf854-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

engine = create_engine(connection_string)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(scope="function")
def db_session():
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
