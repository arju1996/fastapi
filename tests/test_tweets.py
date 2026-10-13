import pytest
from app import models


def test_get_all_tweets(authorized_client, test_tweets):
    res = authorized_client.get("/tweets/")
    def validate(tweet):
        return models.TweetPublic(**tweet)
    
    tweet_map = map(validate, res.json())
    tweet_list = list(tweet_map)
    print("test_get_all_tweets :: tweet_map = ", tweet_list)
    
    assert len(res.json()) == len(test_tweets)
    assert res.status_code == 200

def test_unauthorized_get_tweet(client, test_tweets):
    res = client.get(f"/tweets/{test_tweets[0].id}")
    print("test_unauthorized_get_tweet :: res.json() = ", res.json())
    assert res.status_code == 401
    # i was expecting "could not validate credentials" but fastapi short circuits and automatically responds with "Not authenticated"

def test_authorized_get_tweet(authorized_client, test_tweets):
    res = authorized_client.get(f"/tweets/{test_tweets[0].id}")
    print("test_authorized_get_tweet :: res.json() = ", res.json())
    assert res.status_code == 200

def test_authorized_get_one_tweet_not_exists(authorized_client):
    res = authorized_client.get(f"/tweets/30")
    print("test_authorized_get_one_tweet_not_exists :: res.json() = ", res.json())
    assert res.status_code == 404

def test_get_one_tweet(authorized_client, test_tweets):
    res = authorized_client.get(f"/tweets/{test_tweets[0].id}")
    print("test_authorized_get_tweet :: res.json() = ", res.json())
    tweet = models.TweetPublic(**res.json())
    assert res.status_code == 200
    assert tweet.title == test_tweets[0].title
    assert tweet.content  == test_tweets[0].content

@pytest.mark.parametrize("title, content, validated", [
    ( "new tweet", "this is the new tweet created by me", True),
    ( "new tweet", "this is the new tweet created by me", True),
    ( "new tweet", "this is the new tweet created by me", True),
    ]
)
def test_create_tweet(authorized_client, test_tweets, test_user, title, content, validated):
    post_data = {
                "title": title,
                "content": content,
                "validated": validated
            }
    res = authorized_client.post("/tweets", json=post_data)
    assert res.status_code == 201
    print("res = ", res.json())
    created_tweet = models.TweetPublic(**res.json())
    assert created_tweet.title == title
    assert created_tweet.content == content
    assert created_tweet.validated == validated
    assert created_tweet.owner_id == test_user["id"]


def test_create_tweet_default_validated_true(authorized_client, test_user, test_tweets):
    post_data = {
                "title": "title",
                "content": "content"
            }
    res = authorized_client.post("/tweets", json=post_data)
    assert res.status_code == 201
    print("res = ", res.json())
    created_tweet = models.TweetPublic(**res.json())
    assert created_tweet.title == post_data["title"]
    assert created_tweet.content == post_data["content"]
    assert created_tweet.validated == False
    assert created_tweet.owner_id == test_user["id"]

def test_unauthorized_create_tweet(client, test_tweets):
    post_data = {
                "title": "title",
                "content": "content"
            }
    res = client.post(f"/tweets/", json=post_data)
    print("test_unauthorized_create_tweet :: res.json() = ", res.json())
    assert res.status_code == 401
    # i was expecting "could not validate credentials" but fastapi short circuits and automatically responds with "Not authenticated"

def test_unauthorized_delete_tweet(client, test_tweets):
    res = client.delete(f"/tweets/{test_tweets[0].id}")
    print("test_unauthorized_delete_tweet :: res.json() = ", res.json())
    assert res.status_code == 401
    # i was expecting "could not validate credentials" but fastapi short circuits and automatically responds with "Not authenticated"

def test_delete_tweet(authorized_client, test_tweets, test_user):
    res = authorized_client.delete(f"/tweets/{test_tweets[0].id}")
    assert res.status_code == 204

def test_delete_tweet_non_exist(authorized_client, test_tweets, test_user):
    res = authorized_client.delete(f"/tweets/55555")
    assert res.status_code == 404

def test_delete_someone_elses_tweet(client, authorized_clients):
    print("overrides:", authorized_clients[0].app.dependency_overrides)    
    client1, client2 = authorized_clients
    print("client1 is client2:", client1 is client2)
    print("client1 is client:", client1 is client)
    print("client1 auth:", client1.headers["Authorization"])
    print("client2 auth:", client2.headers["Authorization"])

    post_data = [{
                "title": "title1",
                "content": "content1",
            },
            {
                "title": "title2",
                "content": "content2"
            }
            ]
    res1 = authorized_clients[0].post("/tweets", json=post_data[0])
    assert res1.status_code == 201

    res2 = authorized_clients[1].post("/tweets", json=post_data[1])
    assert res2.status_code == 201


    res3 = authorized_clients[0].delete(f"/tweets/{res2.json()["id"]}")
    assert res3.status_code == 403
    assert res3.json()["detail"] == "not authorized to perform the requested action"

def test_update_tweet(authorized_client, test_user, test_tweets):
    post_data = {
                "title": "title",
                "content": "content",
                "validated": True,
                "media_url": "https://abc/updated_pic.jpg"
            }
    res = authorized_client.put(f"/tweets/{test_tweets[0].id}", json=post_data)
    assert res.status_code == 200
    print("res = ", res.json())
    updated_tweet = models.TweetPublic(**res.json())
    assert updated_tweet.title == post_data["title"]
    assert updated_tweet.content == post_data["content"]
    assert updated_tweet.validated == post_data["validated"]
    assert updated_tweet.owner_id == test_user["id"]

def test_update_other_usrs_tweet(client, authorized_clients):
    print("overrides:", authorized_clients[0].app.dependency_overrides)    
    client1, client2 = authorized_clients
    print("client1 is client2:", client1 is client2)
    print("client1 is client:", client1 is client)
    print("client1 auth:", client1.headers["Authorization"])
    print("client2 auth:", client2.headers["Authorization"])

    post_data = [{
                "title": "title1",
                "content": "content1",
            },
            {
                "title": "title2",
                "content": "content2"
            }
            ]
    res1 = authorized_clients[0].post("/tweets", json=post_data[0])
    assert res1.status_code == 201

    res2 = authorized_clients[1].post("/tweets", json=post_data[1])
    assert res2.status_code == 201


    res3 = authorized_clients[0].put(f"/tweets/{res2.json()["id"]}", json=post_data[0])
    assert res3.status_code == 403
    assert res3.json()["detail"] == "not authorized to perform the requested action"


def test_unauthorized_update_tweet(client, test_tweets):
    post_data = {
                "title": "title",
                "content": "content",
                "validated": True,
                "media_url": "https://abc/updated_pic.jpg"
            }
    res = client.put(f"/tweets/{test_tweets[0].id}", json=post_data)
    print("test_unauthorized_update_tweet :: res.json() = ", res.json())
    assert res.status_code == 401
    # i was expecting "could not validate credentials" but fastapi short circuits and automatically responds with "Not authenticated"


def test_update_tweet_non_exist(authorized_client, test_tweets, test_user):
    post_data = {
                "title": "title",
                "content": "content",
                "validated": True,
                "media_url": "https://abc/updated_pic.jpg"
            }
    res = authorized_client.put(f"/tweets/55555", json=post_data)
    assert res.status_code == 404