from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..database import get_db

router = APIRouter(prefix="/users", tags=['Users'])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut) # add status code to the decorator for default values
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    # Hash the password - user.password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user) # Add the new user to commit
    db.commit() # Commit the new user
    db.refresh(new_user) # Retrieve the new user and save it to the variable again

    return new_user

@router.get('/{id}', response_model=schemas.UserOut) # Response model goes into the route decorator
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id: {id} does not exist!")

    return user