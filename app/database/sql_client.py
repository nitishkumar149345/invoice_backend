from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .constants import (
    DATABASE_HOST,
    DATABASE_NAME,
    DATABASE_PASSWORD,
    DATABASE_USERNAME,
)

url = f'mysql+pymysql://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}'



engine = create_engine(url)

SessionLocal = sessionmaker(bind= engine)
session = SessionLocal()


Base = declarative_base()