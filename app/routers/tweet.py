from fastapi import status, HTTPException, Response, APIRouter
from .. import models

from sqlmodel import Session, select

from ..database import SessionDep

router = APIRouter(
    prefix='/tweets',
    tags=['Tweets']
)

my_posts = []

def findPost(id):
    for p in my_posts:
        if p["id"] == id :
            return p

@router.post("/", status_code= status.HTTP_201_CREATED)
def create_tweet(tweet: models.TweetCreate, session: SessionDep)->models.TweetPublic:
    tweet = models.Tweet.model_validate(tweet)
    session.add(tweet)
    session.commit()
    session.refresh(tweet)
    return tweet

@router.get("/", status_code= status.HTTP_200_OK)
def get_all_tweets(session: SessionDep)->list[models.TweetPublic]:
    tweets = session.exec(select(models.Tweet)).all()
    return tweets

@router.get("/latest")
def get_tweet(response: Response, session: SessionDep)->models.TweetPublic:
    tweet = session.exec(select(models.Tweet).order_by(models.Tweet.created_at.desc())).first()
    return tweet

@router.get("/{id}")
def get_tweet(id:int, session: SessionDep)->models.TweetPublic:
    # tweet = session.exec(select(Tweet).where(Tweet.id == id)).first()
    tweet = session.get(models.Tweet, id)
    if not tweet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"tweett with id: {id} was not found")
    return tweet

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tweet(id: int, response: Response, session: SessionDep)->None:
    deleted_tweet = session.get(models.Tweet, id)
    if not deleted_tweet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"tweet with id: {id} was not found")
    session.delete(deleted_tweet)
    session.commit()
    return

@router.put("/{id}")
def updated_tweet(id: int, tweet: models.TweetCreate, session: SessionDep)->models.TweetPublic:
    tweet_to_update = session.get(models.Tweet, id)
    if not tweet_to_update:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"tweet with id: {id} was not found")

    newtweet = tweet.model_dump()
    tweet_to_update.sqlmodel_update(newtweet)
    session.add(tweet_to_update)
    session.commit()
    session.refresh(tweet_to_update)

    return tweet_to_update

@router.patch("/{id}")
def updated_tweet(id: int, tweet: models.TweetPublic, session: SessionDep)->models.TweetPublic:
    post = findPost(id)  # this is reference, everything in python is ref
    if not post:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"post with id: {id} was not found")
    post.update(tweet.model_dump(exclude_unset=True)) # this looks more like patch than a put to me
    return {"message" : f"post with id: {id} is updated"}


@router.patch("/{id}")
def updated_tweet(id: int, tweet: models.TweetPublic, session: SessionDep)->models.TweetPublic:
    tweet_to_update = session.get(models.Tweet, id)
    if not tweet_to_update:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"tweet with id: {id} was not found")

    newtweet = tweet.model_dump(exclude_unset=True)
    tweet_to_update.sqlmodel_update(newtweet)
    session.add(tweet_to_update)
    session.commit()
    session.refresh(tweet_to_update)

    return tweet_to_update