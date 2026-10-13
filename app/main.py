from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from .database import engine
from .routers import auth, tweet, user, vote

# SQLModel.metadata.create_all(engine)

app = FastAPI()

origins = [
    "http://localhost:8000",
    "http://localhost",
    "127.0.0.1:8000",
    "127.0.0.1",
    "null"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(tweet.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
def read_root():
    return {"hello": "world"}
