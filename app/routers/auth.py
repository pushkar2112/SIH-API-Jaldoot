from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import schemas, models, utils, oauth2
from ..database import get_db

router = APIRouter(tags=['Authentication'])

@router.post('/login', response_model=schemas.Token) # Token response model
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    # OAUth2PasswordRequestForm returns {
    # username : "daghjk"
    # password : "fvahjfv"
    #}
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user: # Check if the user exists (email check)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    # Check if the password is correct (Password check)
    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")

    # Create a Token
    access_token = oauth2.create_access_token(data = {"user_id": user.id})
    
    # Return Token
    return {'access_token' : access_token, "token_type": "bearer"}