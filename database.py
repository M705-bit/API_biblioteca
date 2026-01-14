from sqlmodel import SQLModel, create_engine, Session
import pandas as pd
from models import Book, User, Rating
from schemas import UserCreate, UserLogin

db = create_engine("sqlite:///database.db")

def create_db_and_tables():
    SQLModel.metadata.create_all(db)

def load_initial_data():
    df_books = pd.read_csv("data/Books.csv", sep=";", dtype={"ISBN": str})
    df_ratings = pd.read_csv("data/Ratings.csv", sep=";")
    df_users = pd.read_csv("data/Users.csv", sep=";", dtype={"User_ID": str})

    df_users["Age"] = pd.to_numeric(df_users["Age"], errors="coerce").astype("Int64")

    df_books = df_books.where(pd.notnull(df_books), None)
    df_ratings = df_ratings.where(pd.notnull(df_ratings), None)
    df_users = df_users.where(pd.notnull(df_users), None)

    df_books = df_books.drop_duplicates(subset=["ISBN"])

    with Session(db) as session:
        for _, row in df_books.iterrows():
            session.add(Book.model_validate(row.to_dict()))
        for _, row in df_users.iterrows():
            session.add(User.model_validate(row.to_dict()))
        for _, row in df_ratings.iterrows():
            session.add(Rating.model_validate(row.to_dict()))
        session.commit()

if __name__ == "__main__":
    print("Criando banco e importando dados...")
    create_db_and_tables()
    load_initial_data()
    print("Banco pronto!")

def get_session():
    with Session(db) as session:
        yield session