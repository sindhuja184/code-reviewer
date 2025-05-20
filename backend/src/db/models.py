from sqlmodel import SQLModel, Relationship, Field
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy import Column
from datetime import datetime, date
import uuid
from typing import List, Optional



class CodeReview(SQLModel, table= True):
    __tablename__ = "code_reviews"
    uid: uuid.UUID = Field(
        default_factory= uuid.uuid4, 
        sa_column= Column(
            pg.UUID, 
            primary_key= True
        )
    )
    user_id : uuid.UUID = Field(foreign_key = "users.uid")
    title: str
    code_snippet: str
    review: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    user: Optional["User"] = Relationship(back_populates="code_reviews")



class User(SQLModel, table = True):
    __tablename__ = "users"
    uid: uuid.UUID = Field(
        sa_column = Column(
            pg.UUID,
            nullable = False, 
            primary_key= True,
            default = uuid.uuid4
        )
    )
    username: str
    email: str
    firstname: str
    lastname: str
    role: str = Field(
        sa_column = Column(
            pg.VARCHAR, 
            nullable = False, 
            server_default= "user"
        )
    )
    is_verified: bool = Field(default=False)
    password_hash:str = Field(exclude= True)
    created_at: datetime = Field(sa_column= Column(pg.TIMESTAMP, default= datetime.now))
    updated_at: datetime = Field(sa_column= Column(pg.TIMESTAMP, default= datetime.now))

    code_reviews: List[CodeReview] = Relationship(back_populates="user")  
