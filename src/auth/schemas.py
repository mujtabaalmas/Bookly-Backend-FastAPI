from pydantic import BaseModel, Field
from datetime import datetime, date
import uuid


class UserCreateModel(BaseModel):
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    username: str = Field(max_length=8)
    email: str = Field(max_length=40)
    password: str = Field(min_length=8)


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

class UserloginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=8)

# class  GetAllUserDataModel(UserModel):
#     username: str
#     email: str


