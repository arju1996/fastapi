from sqlmodel import Session, create_engine
from sqlalchemy import URL

from .config import settings

from fastapi import Depends
from sqlmodel import Session
from typing import Annotated



SQL_DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=settings.DATABASE_USERNAME,
    password=settings.DATABASE_PASSWORD,
    host=settings.DATABASE_HOSTNAME,
    database=settings.DATABASE_NAME
)

engine = create_engine(SQL_DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]