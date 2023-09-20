from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from pydantic.types import conint

# Pydantic model to validate the data

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
    latitude: float
    longitude: float

# Update other Post-related schemas as needed.

class PostCreate(PostBase):
    pass

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        orm_mode = True # Used to return the data as a dict

class Post(BaseModel):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut
    title: str
    content: str
    published: bool
    latitude: float
    longitude: float
    image_path: str  # Add this field for the image URL or path

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = "user"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None
