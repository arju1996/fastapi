from datetime import datetime

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel, func, text




class UserBase(SQLModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    created_at: datetime
    # tweets: list["Tweet"]     # keeping this caused userout returns user->list->user

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: EmailStr = Field(unique=True)
    created_at: datetime | None = Field(
        sa_column_kwargs={"server_default":func.now()}
    )
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
    validated: bool = Field(default=False, sa_column_kwargs={"server_default": text("false")})
    media_url: str | None = None
class TweetCreate(TweetBase):
    pass

class TweetPublic(TweetBase):
    id: int
    owner_id: int
    created_at: datetime
    owner : UserOut
class Tweet(TweetBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        sa_column_kwargs={"server_default":func.now()}
    )
    owner_id: int = Field(foreign_key="user.id", ondelete="CASCADE")  #this is ugly, it should habve been User.id instead of user.id but since user is already taken keyword its not possible
    owner: User | None = Relationship(back_populates="tweets")

class TweetWithLikeCount(TweetPublic):
    count: int

class Vote(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE", primary_key=True)
    tweet_id: int = Field(foreign_key="tweet.id", ondelete="CASCADE", primary_key=True)
    vote_up: bool = Field(default=True)

class VotePublic(SQLModel):
    tweet_id: int
    vote_up: bool