from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from datetime import datetime, UTC
from sqlmodel import Field, Relationship, SQLModel

from pydantic import EmailStr




class UserBase(SQLModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    created_at: datetime
    tweets: list["Tweet"]

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    password: str
    tweets: list["Tweet"] = Relationship(back_populates="owner")

class TokenBase(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    id : str
class TweetBase(SQLModel):
    title: str
    content: str
    validated: bool = False
    media_url: str | None = None
    # owner_id: int

class TweetCreate(TweetBase):
    pass

class TweetPublic(TweetBase):
    id: int
    owner_id: int
    created_at: datetime
    owner : UserOut
class Tweet(TweetBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    owner_id: int = Field(default=None, foreign_key="user.id", ondelete="CASCADE")  #this is ugly, it should habve been User.id instead of user.id
    owner: User | None = Relationship(back_populates="tweets")
