from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from models import Book
from schemas import BookCreate
from database import get_session

router = APIRouter()

#adicionando um livr ao banco de dados geral caso ele não exista ainda
@router.post("/books")
async def create_book(item: BookCreate, session: Session = Depends(get_session)):
    # cria o livro
    '''
    item é um schema do tipo BookCreate que contém os dados necessários para criar um novo livro no banco de dados, definimos isso em schemas.py
    dict() converte o objeto Pydantic em um dicionário para facilitar a manipulação dos dados.
    Por que caso não tenha ficado claro, BookCreate é um objeto Pydantic que define a estrutura dos dados necessários para criar um novo livro
    ** é um desempacotador que pega o dicionário retornado por item.dict() e passa seus pares chave-valor como argumentos nomeados para o construtor da classe Book.
    '''
    book = Book(**item.dict())
    if session.get(Book, book.ISBN):
        return {"message": f"Livro com ISBN {book.ISBN} já existe."}
    session.add(book)
    session.commit()
    session.refresh(book)  # agora book.id existe
    return {"message": f"Livro {book.Title} adicionado com sucesso"}



    
""" #acessar um determinado livro da sua biblioteca 
@router.get("/user/{user_id}/books/{book_id}", response_model=Book)
async def get_user_book(user_id: int, book_id: int, session: Session = Depends(get_session)):
    try:
        statement = select(Book).join(UserBooks).where(
            UserBooks.user_id == user_id,
            UserBooks.book_id == book_id
        )
        return session.exec(statement).first()
    except Exception as e:
        return {"message": "Erro ao acessar o livro: " + str(e)}  """
    
#mostrar todos os livros salvos no banco geral
@router.get("/books", response_model=List[Book])
async def list_books(session: Session = Depends(get_session)):
    return session.exec(select(Book)).all()

#mostrar um livro específico
@router.get("/books/title/{book_title}", response_model=Book)
async def get_book_by_title(book_title: str, session: Session = Depends(get_session)):
    book = session.exec(select(Book).where(Book.Title == book_title)).first()
    if not book:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return book

@router.get("/books/isbn/{book_ISBN}", response_model=Book)
async def get_book_by_ISBN(book_ISBN: str, session: Session = Depends(get_session)):
    isbn = book_ISBN.strip()
    book = session.exec(select(Book).where(Book.ISBN == isbn)).first()

    if not book:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return book



""" @router.get("/usersbooks", response_model=List[Book])
async def list_user_books(user_id: int, session: Session = Depends(get_session)):
    statement = select(Book).join(UserBooks).where(UserBooks.user_id == user_id)
    return session.exec(statement).all() """

#atualizar informações de um livro
@router.put("/books/{book_ISBN}")
async def update_book(book_ISBN: str, item: BookCreate, session: Session = Depends(get_session)):
    book = session.get(Book, book_ISBN)
    if not book:
        return {"message": "Livro não encontrado"}
    book_data = item.dict(exclude_unset=True)
    for key, value in book_data.items():
        setattr(book, key, value)
    session.add(book)
    session.commit()
    session.refresh(book)
    return {"message": "Livro atualizado", "book": book}

#excluir um livro do banco geral
@router.delete("/books/{book_ISBN}")
async def delete_book(book_ISBN: str, session: Session = Depends(get_session)):
    book = session.get(Book, book_ISBN)
    if not book:
        return {"message": "Livro não encontrado"}
    session.delete(book)
    session.commit()
    return {"message": "Livro deletado"}