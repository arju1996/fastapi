from datetime import UTC, datetime, timedelta
import jwt
from fastapi import Depends, status, HTTPException

from .config import settings
from . import models, utils
from fastapi.security import OAuth2PasswordBearer

from .database import SessionDep


oath2_scheme = OAuth2PasswordBearer("login")


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_delta
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY ,settings.ALGORITHM)
    return encoded_jwt

def verify_accesss_token(token: str, credentials_exception)->models.TokenData:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY ,settings.ALGORITHM)
        print("decoded jwd get", payload.get("sub"))
        # this would have sub(right now userid string), user_id(int), role, exp
        id: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if id is None:
            raise credentials_exception
        token_data = models.TokenData.model_validate({"id":id})
    except jwt.InvalidTokenError:
        raise credentials_exception
    return token_data

def get_current_user(session: SessionDep, token: str = Depends(oath2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    token = verify_accesss_token(token, credentials_exception)
    current_user = session.get(models.User, token.id)
    return current_user