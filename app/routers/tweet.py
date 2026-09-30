from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import func, select

from sqlalchemy.orm import selectinload

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
def get_all_tweets(session: SessionDep, search: str | None = None, limit:int = 10, skip:int = 0)->list[models.TweetWithLikeCount]:
    # query = select(models.Tweet)
    query = (
        select(models.Tweet, 
        func.count(models.Vote.tweet_id))
        .join(models.Vote, onclause = models.Vote.tweet_id==models.Tweet.id, isouter=True)
        .group_by(models.Tweet.id)
        .options(selectinload(models.Tweet.owner))  # this makes 1(tweets) + n(user) to 1(tweet) + 1(users)
    )
    # query = (
    #     select(models.Tweet, func.count(models.Vote.tweet_id).label("count"))
    #     .outerjoin(models.Vote, onclause=models.Vote.tweet_id == models.Tweet.id)
    #     .options(selectinload(models.Tweet.owner))
    #     .group_by(models.Tweet.id)
    #     .offset(skip)
    #     .limit(limit)
    # )
    if search:
        query = query.where( models.Tweet.title.ilike(f"%{search}%"))
    query = query.offset(skip).limit(limit)
    tweets = session.exec(query).all()


    tweets_with_likescount : list[models.TweetWithLikeCount] = []
    for a, b in tweets:
        tweet_with_like = models.TweetWithLikeCount.model_validate(a, update={"count":b})
        tweets_with_likescount.append(tweet_with_like)
    return tweets_with_likescount

    return [
        models.TweetWithLikeCount.model_validate(tweet, update={"count": count})
        for tweet, count in tweets
    ]

@router.get("/latest")
def get_tweet(session: SessionDep)->models.TweetPublic:
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
def delete_tweet(id: int, session: SessionDep, user: models.User = Depends(oauth2.get_current_user))->None:
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