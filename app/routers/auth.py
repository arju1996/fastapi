from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from sqlmodel import select

from .. import models, utils, oauth2
from ..database import SessionDep

router = APIRouter(
    tags=['Authentication']
)

@router.post("/login")
# def login(creds: models.UserCreate, session: SessionDep)->models.TokenBase:
def login(session: SessionDep, creds: OAuth2PasswordRequestForm = Depends())->models.TokenBase:
    user = session.exec(select(models.User).where(models.User.email == creds.username)).first() # since its a form there is no email, and i have to read email from username
    if not user:
        raise HTTPException(status.HTTP_403_FORBIDDEN, f"Invalid credentials")
    if not utils.verify(creds.password, user.password):
        raise HTTPException(status.HTTP_403_FORBIDDEN, f"Invalid credentials")
    
    payload = {
        "sub": str(user.id),
        "user_id": user.id,
        "role": "user"
    }
    token = oauth2.create_access_token(payload)

    return models.TokenBase.model_validate({
        "access_token":token,
        "token_type":"bearer"
    })