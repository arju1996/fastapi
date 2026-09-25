from fastapi import status, HTTPException, APIRouter, Depends
from .. import models, utils, oauth2

from ..database import SessionDep


router = APIRouter(
    prefix='/users',
    tags=['Users']
)

@router.post("/", status_code= status.HTTP_201_CREATED)
def create_user(user: models.UserCreate, session: SessionDep)->models.UserOut:
    user.password = utils.hash(user.password)
    new_user = models.User.model_validate(user)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@router.get("/{id}", status_code= status.HTTP_200_OK)
def get_user(id: int, session: SessionDep, user_id:int = Depends(oauth2.get_current_user))->models.UserOut:

    user = session.get(models.User, id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"user with id: {id} was not found")

    return user