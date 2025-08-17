from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


engine = create_engine("postgresql+psycopg2://scott:tiger@localhost/")

SessionLocal = sessionmaker(engine)
