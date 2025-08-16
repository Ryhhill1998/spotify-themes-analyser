from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()

engine = create_engine("postgresql+psycopg2://scott:tiger@localhost/")

SessionLocal = sessionmaker(engine)
