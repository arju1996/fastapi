from fastapi import FastAPI, status, Response, HTTPException
from fastapi.param_functions import Body 

from random import randrange

import psycopg
import time
from psycopg.rows import dict_row
from sqlmodel import SQLModel

from .database import engine
from .database import get_session
from sqlmodel import Session, select

from fastapi import Depends

from .models import Tweet

from fastapi import Depends
from typing import Annotated

my_posts = []

def findPost(id):
    for p in my_posts:
        if p["id"] == id :
            return p

SQLModel.metadata.create_all(engine)
SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

while True:
    try:
        conn = psycopg.connect("host=localhost dbname=fastapi user=postgres password='1441'", row_factory=dict_row)
        cur  = conn.cursor()
        print("database connection was succesful")
        break

        # with psycopg.connect("host=localhost dbname=fastapi user=postgres password='1441'", row_factory=dict_row) as conn:
        #     with conn.cursor() as cur:
        #         print("database connection was succesful")
        #         break
    except Exception as error:
        print("connection to db failed")
        print("error: ", error)
        time.sleep(2)

@app.get("/")
def read_root():
    return {"hello", "world"}

@app.post("/tweet", status_code= status.HTTP_201_CREATED)
def create_tweet(tweet: Tweet, session: SessionDep)->Tweet:
    tweet = Tweet(title = tweet.title, content = tweet.content, validated = tweet.validated, media_url= tweet.media_url)
    session.add(tweet)
    session.commit()
    session.refresh(tweet)
    return tweet

@app.get("/tweets", status_code= status.HTTP_200_OK)
def get_all_tweets(session: SessionDep)->list[Tweet]:
    tweets = session.exec(select(Tweet)).all()
    return tweets

@app.get("/tweet/latest")
def get_tweet(response: Response, session: SessionDep)->Tweet:
    tweet = session.exec(select(Tweet).order_by(Tweet.created_at.desc())).first()
    return tweet

@app.get("/tweet/{id}")
def get_tweet(id:int, session: SessionDep)->Tweet:
    # tweet = session.exec(select(Tweet).where(Tweet.id == id)).first()
    tweet = session.get(Tweet, id)
    if not tweet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"tweett with id: {id} was not found")
    return tweet

@app.delete("/tweet/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tweet(id: int, response: Response, session: SessionDep)->None:
    deleted_tweet = session.get(Tweet, id)
    if not deleted_tweet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"tweet with id: {id} was not found")
    session.delete(deleted_tweet)
    session.commit()
    return

@app.put("/tweet/{id}")
def updated_tweet(id: int, tweet: Tweet, session: SessionDep)->Tweet:
    tweet_to_update = session.get(Tweet, id)
    if not tweet_to_update:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"tweet with id: {id} was not found")

    newtweet = tweet.model_dump()
    tweet_to_update.sqlmodel_update(newtweet)
    session.add(tweet_to_update)
    session.commit()
    session.refresh(tweet_to_update)

    return tweet_to_update

@app.patch("/tweet/{id}")
def updated_tweet(id: int, tweet: Tweet, session: SessionDep)->Tweet:
    post = findPost(id)  # this is reference, everything in python is ref
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"post with id: {id} was not found")
    post.update(tweet.model_dump(exclude_unset=True)) # this looks more like patch than a put to me
    return {"message" : f"post with id: {id} is updated"}


@app.patch("/tweet/{id}")
def updated_tweet(id: int, tweet: Tweet, session: SessionDep)->Tweet:
    tweet_to_update = session.get(Tweet, id)
    if not tweet_to_update:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"tweet with id: {id} was not found")

    newtweet = tweet.model_dump(exclude_unset=True)
    tweet_to_update.sqlmodel_update(newtweet)
    session.add(tweet_to_update)
    session.commit()
    session.refresh(tweet_to_update)

    return tweet_to_update