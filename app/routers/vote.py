from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import select

from .. import models, oauth2
from ..database import SessionDep


router = APIRouter(
    prefix='/votes',
    tags=["votes"]
)

#no validation for whats inside the body?

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote_given: models.VotePublic, session: SessionDep, user:models.User = Depends(oauth2.get_current_user))->models.VotePublic:

    tweet = session.exec(select(models.Tweet).where(models.Tweet.id == vote_given.tweet_id)).first()
    if tweet is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"tweett with id: {id} was not found")


    # if exists, and if same sign => delete
    # if doesnt exists => set whatever sign we got.
    vote_db = session.exec(select(models.Vote).where(models.Vote.tweet_id == vote_given.tweet_id, models.Vote.user_id == user.id)).first()
    if vote_db is None:
        vote_given_dict = vote_given.model_dump(exclude_unset=True)
        vote_given_dict.update({"user_id": user.id})
        vote = models.Vote(**vote_given_dict)
        session.add(vote)
        session.commit()
        session.refresh(vote)
        vote_db = vote
    else:
        if vote_given.vote_up == vote_db.vote_up :
            session.delete(vote_db)
            session.commit()
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            vote_db.vote_up = vote_given.vote_up
            session.add(vote_db)
            session.commit()
            session.refresh(vote_db)

    return vote_db