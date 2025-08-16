from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql+psycopg2://scott:tiger@localhost/")

SessionLocal = sessionmaker(engine)
