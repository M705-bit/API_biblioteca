from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from models import User, Book, Rating
from schemas import UserCreate, RatingCreate
from database import get_session

router = APIRouter()

#adicionar uma avaliação para um livro por um usuário
""" @router.post("/ratings")
async def create_rating(user_id: int, book_ISBN: str, rating_value: int, session: Session = Depends(get_session)):
    rating = Rating(user_id=user_id, book_ISBN=book_ISBN, rating=rating_value)
    session.add(rating)
    session.commit()
    session.refresh(rating)
    return {"message": "Rating created", "rating": rating} """

@router.post("/ratings")
async def create_rating(item: RatingCreate, session: Session = Depends(get_session)):
    rating = Rating(**item.dict())
    session.add(rating)
    session.commit()
    session.refresh(rating)
    return {"message": "Rating created", "rating": rating}



#obter todas as avaliações de um usuário
@router.get("/users/{user_id}/ratings", response_model=List[Rating])
async def get_user_ratings(user_id: int, session: Session = Depends(get_session)):
    statement = select(Rating).where(Rating.user_id == user_id)
    return session.exec(statement).all()

@router.put("/ratings/{user_id}/{book_ISBN}")
async def update_rating(user_id: int, book_ISBN: str, rating_value: int, session: Session = Depends(get_session)):
    rating = session.exec(select(Rating).where(Rating.user_id == user_id, Rating.book_ISBN == book_ISBN)).first()
    if not rating:
        return {"message": "Rating not found"}
    rating.rating = rating_value
    session.add(rating)
    session.commit()
    session.refresh(rating)
    return {"message": "Rating updated", "rating": rating}

@router.delete("/ratings/{user_id}/{book_ISBN}")
async def delete_rating(user_id: int, book_ISBN: str, session: Session = Depends(get_session)):
    rating = session.exec(select(Rating).where(Rating.user_id == user_id, Rating.book_ISBN == book_ISBN)).first()
    if not rating:
        return {"message": "Rating not found"}
    session.delete(rating)
    session.commit()
    return {"message": "Rating deleted"}