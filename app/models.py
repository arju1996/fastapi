from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from datetime import datetime, UTC
from sqlmodel import Field, SQLModel


class TweetBase(SQLModel):
    title: str
    content: str
    validated: bool = False
    media_url: str | None = None

class TweetCreate(TweetBase):
    pass

class TweetPublic(TweetBase):
    id: int
    created_at: datetime

class Tweet(TweetBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))