from typing import Optional
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    User_ID: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str

class Book(SQLModel, table=True):
    Book_ID: Optional[int] = Field(default=None, primary_key=True)
    ISBN: str = Field(primary_key=True)
    Title: str
    Author: str | None = None
    Year: int | None = None
    Publisher: str  | None = None
    

class Rating(SQLModel, table=True):
    User_ID: int = Field(foreign_key="user.User_ID", primary_key=True)
    ISBN: str = Field(foreign_key="book.ISBN", primary_key=True)
    Rating: int

