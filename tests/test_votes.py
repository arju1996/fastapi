import pytest
from app import models

@pytest.fixture()
def test_vote(test_tweets, session, test_user):
    vote = models.Vote(user_id=test_user["id"], tweet_id=test_tweets[0].id, vote_up=True)
    session.add(vote)
    session.commit()

def test_votes_on_tweet(authorized_client, test_tweets):
    res = authorized_client.post("votes", json={"tweet_id":test_tweets[0].id, "vote_up":True})
    assert res.status_code == 201

def test_unauthorized_votes_on_tweet(client, test_tweets):
    res = client.post("votes", json={"tweet_id":test_tweets[0].id, "vote_up":True})
    assert res.status_code == 401

def test_double_vote_on_tweet(test_vote, test_tweets, authorized_client):
    res = authorized_client.post("votes", json={"tweet_id":test_tweets[0].id, "vote_up":True})
    assert res.status_code == 204

def test_votes_on_not_exist_tweet(authorized_client, test_tweets):
    res = authorized_client.post("votes", json={"tweet_id":12345, "vote_up":True})
    assert res.status_code == 404