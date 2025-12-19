from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from typing import List
from models import User, Book, Rating
from schemas import UserCreate
from database import get_session

router = APIRouter()
#cadastrar um novo usuário
@router.post("/users")
async def create_user(item: UserCreate, session: Session = Depends(get_session)):
    user = User(**item.dict())
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "Usuário criado", "user_id": user.User_ID}

#mostrar os usuários cadastrados
@router.get("/users", response_model=List[User])
async def list_users(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()

#mostrar os livros que estão na biblioteca do usuário
@router.get("/users/{user_id}")
async def profile(user_id: int, session: Session = Depends(get_session)):
    # primeiro seleciona os ISBNs avaliados pelo usuário
    subquery = select(Rating.ISBN).where(Rating.User_ID == user_id)
    
    # depois busca os livros correspondentes
    statement = select(Book).where(Book.ISBN.in_(subquery))
    results = session.exec(statement).all()
    
    return {"books": results}

#atualizar dados do usuário
@router.put("/users/{user_id}")
async def update_user(user_id: int, item: UserCreate, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        return {"message": "Usuário não encontrado"}
    user_data = item.dict(exclude_unset=True)
    for key, value in user_data.items():
        setattr(user, key, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "Usuário atualizado", "user": user}

#excluir um usuário do sistema
@router.delete("/users/{user_id}")
async def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        return {"message": "Usuário não encontrado"}
    session.delete(user)
    session.commit()
    return {"message": "Usuário deletado"}