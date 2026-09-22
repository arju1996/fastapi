from fastapi import FastAPI, status, Response, HTTPException
from fastapi.param_functions import Body 

from pydantic import BaseModel
from datetime import datetime

from typing import Optional
from random import randrange

import psycopg
import time
from psycopg.rows import dict_row
class Tweet(BaseModel):
    title: str
    content: str
    validated: bool = False
    media_url: str | None = None
    created_at: Optional[datetime] = None #optinal is older way


my_posts = []

def findPost(id):
    for p in my_posts:
        if p["id"] == id :
            return p

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
def create_tweet(tweet: Tweet):
    # time = datetime.now()
    cur.execute("INSERT INTO tweets (title, content, validated, media_url) VALUES (%s, %s, %s, %s) returning *", (tweet.title, tweet.content, tweet.validated, tweet.media_url))    #parameters has to be in a tuple or list ie (id, ) or (id, id2) or []
    created_tweet = cur.fetchone()
    conn.commit()
    return {"data": created_tweet}

@app.get("/tweets", status_code= status.HTTP_200_OK)
def get_all_tweets():
    cur.execute("SELECT * FROM tweets")
    tweets = cur.fetchall()
    return {"data": tweets}

@app.get("/tweet/latest")
def get_tweet(response: Response):
    cur.execute("SELECT * FROM tweets order by created_at")
    tweet = cur.fetchone()
    print(tweet)
    return {"post_detail": tweet}

@app.get("/tweet/{id}")
def get_tweet(id:int):
    cur.execute("SELECT * FROM tweets where id = %s", (id,))    #parameters has to be in a tuple or list ie (id, ) or (id, id2) or []
    tweet = cur.fetchone()
    if not tweet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"post with id: {id} was not found")
    return {"detail": tweet}

@app.delete("/tweet/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tweet(id: int, response: Response):
    cur.execute("DELETE FROM tweets where id = %s  returning *", (id, ))
    deleted_post = cur.fetchone()
    conn.commit() # why do i not need commit in delete?
    if not deleted_post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"post with id: {id} was not found")
    return

@app.put("/tweet/{id}")
def updated_tweet(id: int, tweet: Tweet):
    cur.execute("UPDATE tweets SET title = %s, content = %s, validated = %s, media_url = %s  WHERE ID = %s returning *", (tweet.title, tweet.content, tweet.validated, tweet.media_url, id))
    updated_tweet = cur.fetchone()
    
    if not updated_tweet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"post with id: {id} was not found")
    return {"data" : updated_tweet}


@app.patch("/tweet/{id}")
def updated_tweet(id: int, tweet: Tweet):
    post = findPost(id)  # this is reference, everything in python is ref
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"post with id: {id} was not found")
    post.update(tweet.model_dump(exclude_unset=True)) # this looks more like patch than a put to me
    return {"message" : f"post with id: {id} is updated"}
