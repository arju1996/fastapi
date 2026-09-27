from fastapi import FastAPI
from sqlmodel import SQLModel

from .database import engine
from .routers import auth, tweet, user

SQLModel.metadata.create_all(engine)

app = FastAPI()

app.include_router(tweet.router)
app.include_router(user.router)
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"hello", "world"}
