import token
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from models import User, Book, Rating
from schemas import UserCreate, UserLogin
from database import get_session
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

@router.post("/register")
def register(user: UserCreate, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == user.username)
    existing_user = session.exec(statement).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    db_user = User(
        username=user.username,
        password=pwd_context.hash(user.password)
    )

    session.add(db_user)
    session.commit()

    return {"message": "User created successfully"}

@router.post("/login")
def login(user: UserLogin, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == user.username)
    existing_user = session.exec(statement).first()

    if not existing_user or not pwd_context.verify(user.password, existing_user.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    return {"message": "Login successful"}

#mostrar TODOS os usuários cadastrados
@router.get("/users", response_model=List[User])
async def list_users(session: Session = Depends(get_session)):
    return session.exec(select(User)).all()

#mostrar um usuário específico pelo ID
# uma requisição para essa rota é "GET /users/{user_id}"

@router.get("/users/{user_id}", response_model=User)
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(404, "Usuário não encontrado")
    return user

#mostrar os livros que foram avaliados por um usuário
#exemplo de requisição: GET /users/{user_id}/books

@router.get("/users/{user_id}/books", response_model=List[Book])
def get_user_books(user_id: int, session: Session = Depends(get_session)):
    subquery = select(Rating.ISBN).where(Rating.User_ID == user_id)
    statement = select(Book).where(Book.ISBN.in_(subquery))
    return session.exec(statement).all()


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