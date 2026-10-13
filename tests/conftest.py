import pytest
from fastapi.testclient import TestClient
from sqlalchemy import URL
from sqlmodel import SQLModel, Session, create_engine

from app.config import settings
from app.database import get_session
from app.main import app
from app.oauth2 import create_access_token
from app import models


SQL_DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=settings.DATABASE_USERNAME,
    password=settings.DATABASE_PASSWORD,
    host=settings.DATABASE_HOSTNAME,
    database=settings.DATABASE_NAME+"_test",
    port=settings.DATABASE_PORT
)


engine = create_engine(SQL_DATABASE_URL)

@pytest.fixture(scope="function")
def session():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def client(session):
    def get_session_test():
        with Session(engine) as session:
            yield session
    app.dependency_overrides[get_session] = get_session_test
    yield TestClient(app)

@pytest.fixture(scope="function")
def test_user(client):
    user_data = {"email":"arjuntt500@gmail.com", "password":"Arjun@1996"}
    res = client.post("/users", json=user_data)
    assert res.status_code == 201

    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user

@pytest.fixture(scope="function")
def token(test_user):
    payload = {
        "sub": str(test_user["id"]),
        "user_id": test_user["id"],
        "role": "user"
    }
    return create_access_token(payload)


@pytest.fixture(scope="function")
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client


@pytest.fixture(scope="function")
def test_tweets(session, test_user):
    tweet_data = [
        {
        "title": "first title",
        "content": "first comment",
        "owner_id": test_user["id"],
        },
        {
        "title": "second title",
        "content": "second comment",
        "owner_id": test_user["id"],
        },
        {
        "title": "second title",
        "content": "second comment",
        "owner_id": test_user["id"],
        }
    ]
    tweet_data_map = [
        {
        "title": "first title",
        "content": "first comment",
        "owner_id": test_user["id"],
        }
    ]

    def create_tweets_model(tweet_data):
        return models.Tweet(**tweet_data)

    tweet_map = map(create_tweets_model, tweet_data)
    tweet = list(tweet_map)

    session.add_all(tweet)
    session.commit()
    tweets = session.query(models.Tweet).all()
    print("tweets = ", tweets)
    return tweets

# my multiple user flow starts here
@pytest.fixture(scope="function")
def test_users(client):
    user_data = [{"email":"arjuntt500@gmail.com", "password":"Arjun@1996"}, {"email":"arjuntt@yahoo.com", "password":"Arjun@2026"}]
    users_list = []

    res = client.post("/users", json=user_data[0])
    assert res.status_code == 201

    new_user = res.json()
    new_user['password'] = user_data[0]['password']

    users_list.append(new_user)

    res = client.post("/users", json=user_data[1])
    assert res.status_code == 201

    new_user = res.json()
    new_user['password'] = user_data[1]['password']

    users_list.append(new_user)
    return users_list

@pytest.fixture(scope="function")
def tokens(test_users):
    payload = {
        "sub": str(test_users[0]["id"]),
        "user_id": test_users[0]["id"],
        "role": "user"
    }
    token1 = create_access_token(payload)
    payload = {
        "sub": str(test_users[1]["id"]),
        "user_id": test_users[1]["id"],
        "role": "user"
    }
    token2 = create_access_token(payload)
    return [token1, token2]

@pytest.fixture(scope="function")
def authorized_clients(client, tokens):
    return [
        TestClient(app, headers = {"Authorization": f"Bearer {token}"})
        for token in tokens
    ]