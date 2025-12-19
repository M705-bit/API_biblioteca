from typing import Optional
from pydantic import BaseModel

class UserCreate(BaseModel):
    User_ID: int | None = None
    Age: int
    #username: str
    #email: str
    #hashed_password: str

class BookCreate(BaseModel):
    ISBN: str 
    Title: str
    Author: str | None = None
    Year: int | None = None
    Publisher: str  | None = None

class RatingCreate(BaseModel):
    User_ID: int
    ISBN: str
    Rating: int

