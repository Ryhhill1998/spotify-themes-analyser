from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.db import Base

connection_string = "postgresql://neondb_owner:npg_XV9fA5MKUGlD@ep-rapid-cell-abkxf854-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

engine = create_engine(connection_string)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@contextmanager
def get_db_session():
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
