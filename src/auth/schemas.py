from pydantic import BaseModel, Field, EmailStr, constr
from src.books.schemas import BookModel
from src.reviews.schemas import ReviewModel
from datetime import datetime, date
from typing import List, Optional
import uuid


class UserCreateModel(BaseModel):
    first_name: constr(min_length=1, max_length=25)
    last_name: constr(min_length=1, max_length=25)
    username: constr(min_length=3, max_length=8)
    email: EmailStr
    password: constr(min_length=8)


class UserModel(BaseModel):

    uid: uuid.UUID
    username: str
    email: str
    password_hash: str = Field(exclude=True)
    first_name: str
    last_name: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class UserBooksModel(UserModel):

    books: Optional[List[BookModel]]
    reviews: Optional[List[ReviewModel]]


class UserloginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=8)


class EmailModel(BaseModel):
    addresses: List[str]


class PasswordResetRequestModel(BaseModel):
    email: str


class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str
