import jwt
import pytest
from sqlmodel import select

from app import models
from app.config import settings


def test_root(client):
    res = client.get("/")
    assert res.json().get("hello") == "world"
    assert (res.status_code == 200)

def test_user2(client):
    res = client.post("/users", json={
        "email":"arjuntt5000000@gmail.com",
        "password":"Arjun@1996"
        }
    )
    new_user = models.UserOut.model_validate(res.json())
    assert new_user is not None

def test_user_2(client, session):
    res = client.post("/users", json={
        "email":"arjuntt500@gmail.com",
        "password":"Arjun@1996"
        }
    )
    assert res.status_code == 201
    statement = select(models.User).where(models.User.email == "arjuntt500@gmail.com")
    db_user = session.exec(statement).first()
    assert db_user is not None
    assert db_user.email == "arjuntt500@gmail.com"
    

def test_user_login(client, session, test_user):
    res = client.post("/login", data={
        "username": test_user["email"],
        "password": test_user["password"]
        }
    )
    token = models.TokenBase.model_validate(res.json())
    print("token = ", token)
    assert token is not None
    assert token.access_token is not None
    # verify jwt is valid
    payload = jwt.decode(token.access_token, settings.SECRET_KEY, [settings.ALGORITHM])
    print("decoded jwd get", payload.get("sub"))
    id: str = payload.get("sub")
    user_id: int = payload.get("user_id")
    assert(user_id == test_user["id"])

@pytest.mark.parametrize("email, password, status_code", [
    ("arjuntt500@gmail.com", "Arjun@199", 401),
    ("arjuntt500@gmail.co", "Arjun@1996", 401),
    ("arjuntt500@gmail.com", None, 422),
    (None, "Arjun@1996", 422),
])
def test_incorrect_login(client, test_user, email, password, status_code):
    res = client.post("/login", data={
        "username": email,
        "password": password
        }
    )
    print("res.json() = ", res.json())
    assert(res.status_code == status_code)
    # assert(res.json().get('detail') == 'Invalid credentials') #because for 422 there wont be this details