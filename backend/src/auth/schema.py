from pydantic import BaseModel, Field
import uuid
from datetime import date, datetime
from typing import List , Optional

class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    firstname: str
    lastname: str
    is_verified: bool = Field(default=False)
    password_hash:str = Field(exclude= True)
    created_at: datetime
    updated_at: datetime 
    

class UserCreateModel(BaseModel):
    firstname : str = Field(max_length= 25)
    lastname : str =  Field(max_length= 25)
    username: str = Field(max_length= 8)
    email: str = Field(max_length = 40)
    password: str = Field(max_length=20)
    role: Optional[str] = "user"

class UserLoginModel(BaseModel):
    username: str = Field(max_length= 40)
    password: str = Field(min_length= 6)

class UsernameModel(BaseModel):
    username: str


class PasswordResetRequestModel(BaseModel):
    email: str

class PasswordResetConfirmModel(BaseModel):
    new_password : str
    confirm_password : str

