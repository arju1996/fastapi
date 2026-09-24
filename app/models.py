from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from datetime import datetime, UTC
from sqlmodel import Field, SQLModel


# class Tweet(BaseModel):
#     title: str
#     content: str
#     validated: bool = False
#     media_url: str | None = None
#     created_at: Optional[datetime] = None #optinal is older way



# class Posttest(SQLModel, table=True):
#     id: int | None = Field(default=None, primary_key=True)
#     heading: str
#     content: str
#     verified: bool = False
#     attachments: str = None
#     dob: datetime | None = Field(default=None)

class Tweet(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    content: str
    validated: bool = False
    media_url: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))