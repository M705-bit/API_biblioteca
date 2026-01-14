from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from models import Book
from schemas import BookCreate
from database import get_session
from serviceBooks import fetch_books_by_title

router = APIRouter()

@router.get("/import/title")
def import_books_by_title(title: str):
    return fetch_books_by_title(title)

@router.post("/books")
async def create_book(item: BookCreate, session: Session = Depends(get_session)):
    book = Book(**item.dict())
    if session.get(Book, book.ISBN):
        return {"message": f"Livro com ISBN {book.ISBN} já existe."}
    session.add(book)
    session.commit()
    session.refresh(book)  
    return {"message": f"Livro {book.Title} adicionado com sucesso a sua coleção.", "book": book}

#mostrar todos os livros salvos no banco geral
@router.get("/books", response_model=List[Book])
async def list_books(session: Session = Depends(get_session)):
    return session.exec(select(Book)).all()

# a rota precisa ser chamada assim: /books/search?query=O%20Senhor%20dos%20Anéis
@router.get("/books/title/search")
def search_books_by_title(query: str, session: Session = Depends(get_session)):
    statement = select(Book).where(Book.Title.ilike(f"%{query}%"))
    if not statement:
        """ #tenta autor
        chamada_api = import_books_by_title(query)
        if chamada_api:
            for item in chamada_api:
                book = Book(**item)
                if not session.get(Book, book.ISBN):
                    session.add(book)
            session.commit()
            #depois de importar, faz a busca novamente no banco local
            statement = select(Book).where(Book.Title.ilike(f"%{query}%"))
            books = session.exec(statement).all()
            return books """
        return {"message": "Nenhum livro encontrado com esse título."}
    else:
        books = session.exec(statement).all()
        return books

@router.get("/books/author/search")
def search_books_by_author(author: str, session: Session = Depends(get_session)):
    statement = select(Book).where(Book.Author.ilike(f"%{author}%"))
    if not statement:
        return {"message": "Nenhum livro encontrado com esse autor."}
    else:
        books = session.exec(statement).all()
        return books

@router.get("/books/publisher/search")
def search_books_by_publisher(publisher: str, session: Session = Depends(get_session)):
    statement = select(Book).where(Book.Publisher.ilike(f"%{publisher}%"))
    if not statement:
        return {"message": "Nenhum livro encontrado com essa editora."}
    else:
        books = session.exec(statement).all()
        return books

#exibir informações de um livro específico a partir do id 
@router.get("/books/{id}", response_model=Book)
async def get_book_by_id(id: int, session: Session = Depends(get_session)):
    book = session.exec(select(Book).where(Book.Book_ID == id)).first()
    if not book:
        raise HTTPException(status_code=404, detail="Livro não encontrado")
    return book

#atualizar informações de um livro
@router.put("/books/{id}")
async def update_book(id: int, item: BookCreate, session: Session = Depends(get_session)):
    book = session.get(Book, id)
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