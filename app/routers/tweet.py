from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import select

from .. import oauth2, models
from ..database import SessionDep

router = APIRouter(
    prefix='/tweets',
    tags=['Tweets']
)

@router.post("/", status_code= status.HTTP_201_CREATED)
def create_tweet(tweet: models.TweetCreate, session: SessionDep, user: models.User = Depends(oauth2.get_current_user))->models.TweetPublic:
    # if not authenticated it should throw error before reaching here
    # cant use model validate, as created_at has to come from db, and created_at is not nullable
    # tweet = models.Tweet.model_validate(tweet, update={"owner_id":user.id})
    tweet = tweet.model_dump(exclude_unset=True)
    tweet.update({"owner_id":user.id})
    db_tweet = models.Tweet(**tweet)
    session.add(db_tweet)
    session.commit()
    session.refresh(db_tweet)
    return db_tweet

@router.get("/", status_code= status.HTTP_200_OK)
def get_all_tweets(session: SessionDep)->list[models.TweetPublic]:
    tweets = session.exec(select(models.Tweet)).all()
    return tweets

@router.get("/latest")
def get_tweet(response: Response, session: SessionDep)->models.TweetPublic:
    tweet = session.exec(select(models.Tweet).order_by(models.Tweet.created_at.desc())).first()
    return tweet

@router.get("/{id}")
def get_tweet(id:int, session: SessionDep, user: models.User = Depends(oauth2.get_current_user))->models.TweetPublic:
    # tweet = session.exec(select(Tweet).where(Tweet.id == id)).first()
    tweet = session.get(models.Tweet, id)
    if not tweet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"tweett with id: {id} was not found")
    return tweet

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tweet(id: int, response: Response, session: SessionDep, user: models.User = Depends(oauth2.get_current_user))->None:
    deleted_tweet = session.get(models.Tweet, id)
    if not deleted_tweet:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"tweet with id: {id} was not found")
    if deleted_tweet.owner_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, f"not autherized to perform the requested action")
    session.delete(deleted_tweet)
    session.commit()
    return

@router.put("/{id}")
def updated_tweet(id: int, tweet: models.TweetCreate, session: SessionDep, user: models.User = Depends(oauth2.get_current_user))->models.TweetPublic:
    tweet_to_update = session.get(models.Tweet, id)
    if not tweet_to_update:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"tweet with id: {id} was not found")
    if tweet_to_update.owner_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, f"not autherized to perform the requested action")
    newtweet = tweet.model_dump()
    tweet_to_update.sqlmodel_update(newtweet)
    session.add(tweet_to_update)
    session.commit()
    session.refresh(tweet_to_update)

    return tweet_to_update


@router.patch("/{id}")
def updated_tweet(id: int, tweet: models.TweetPublic, session: SessionDep, user: models.User = Depends(oauth2.get_current_user))->models.TweetPublic:
    tweet_to_update = session.get(models.Tweet, id)
    if not tweet_to_update:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"tweet with id: {id} was not found")
    if tweet_to_update.owner_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, f"not autherized to perform the requested action")

    newtweet = tweet.model_dump(exclude_unset=True)
    tweet_to_update.sqlmodel_update(newtweet)
    session.add(tweet_to_update)
    session.commit()
    session.refresh(tweet_to_update)

    return tweet_to_update