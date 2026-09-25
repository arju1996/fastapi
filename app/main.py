from fastapi import FastAPI, status, Response, HTTPException
from fastapi.param_functions import Body 

from random import randrange

import psycopg
import time
from psycopg.rows import dict_row
from sqlmodel import SQLModel

from .database import engine
from sqlmodel import Session, select


from .models import Tweet, TweetCreate, TweetPublic, User, UserCreate, UserOut


from . import utils

from .routers import tweet, user, auth

SQLModel.metadata.create_all(engine)

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

app.include_router(tweet.router)
app.include_router(user.router)
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"hello", "world"}
