from fastapi import FastAPI, status, Response, HTTPException
from fastapi.param_functions import Body 
from pydantic import BaseModel
from typing import Optional
from random import randrange
class Tweet(BaseModel):
    title: str
    content: str
    defaultField: bool = True
    optionalField: Optional[int] = None


my_posts = []

def findPost(id):
    for p in my_posts:
        if p["id"] == id :
            return p

app = FastAPI()

@app.get("/")
def read_root():
    return {"hello", "world"}

@app.post("/tweet", status_code= status.HTTP_201_CREATED)
def create_tweet(tweet: Tweet):
    body = tweet.model_dump()
    body["id"] = randrange(0, 100000)
    my_posts.append(body)
    return {"inserted": body}

@app.get("/tweets", status_code= status.HTTP_200_OK)
def get_all_tweets():
    return {"all_posts": my_posts}

@app.get("/tweet/latest")
def get_tweet(response: Response):
    post = my_posts[-1:]
    print(post)
    if not post:
        response.status_code = status.HTTP_404_NOT_FOUND #throwing http exception is the better option
        return {"post_details": ""}
    return {"post_detail": post}

@app.get("/tweet/{id}")
def get_tweet(id:int):
    post = findPost(id)
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"post with id: {id} was not found")
    return {"detail": post}

@app.delete("/tweet/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tweet(id: int, response: Response):
    post = findPost(id)
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"post with id: {id} was not found")
    my_posts.remove(post)
    return

@app.put("/tweet/{id}")
def updated_tweet(id: int, tweet: Tweet):
    post = findPost(id)  # this is reference, everything in python is ref
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"post with id: {id} was not found")
    post.update(tweet.model_dump(exclude_unset=True)) # this looks more like patch than a put to me
    return {"message" : f"post with id: {id} is updated"}
