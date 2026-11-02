# API Biblioteca 📚☕📑

A RESTful API for library management built with **FastAPI** and **Python 3.11**, backed by a **SQLite** database and populated with real-world book, user, and rating datasets.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Data Models](#data-models)
- [API Endpoints](#api-endpoints)
- [External Integrations](#external-integrations)
- [Frontend](#frontend)
- [Getting Started](#getting-started)
- [Running with Docker](#running-with-docker)
- [Dataset](#dataset)
- [Known Limitations](#known-limitations)

---

## Overview

API Biblioteca is a library management system that allows users to register, browse books, and submit ratings.

- User registration and authentication with hashed passwords
- Full CRUD operations for books, users, and ratings
- Full-text search across book titles, authors, and publishers
- Integration with the **Google Books API** to import new book entries
- A minimal HTML/JS frontend served directly by the FastAPI app
- Docker support for containerized deployment

---

## Project Structure

```
API_biblioteca/
├── main.py                 # FastAPI app factory, startup events, router registration
├── models.py               # SQLModel ORM model definitions (User, Book, Rating)
├── schemas.py              # Pydantic request/response schemas
├── database.py             # Database engine, session factory, table creation
├── serviceBooks.py         # Google Books API integration service
├── requirements.txt        # Python dependency pinning
├── Dockerfile              # Container build instructions
├── .dockerignore           # Files excluded from Docker build context
│
├── routers/
│   ├── users.py            # User management endpoints (/register, /login, /users)
│   ├── books.py            # Book CRUD and search endpoints (/books)
│   └── ratings.py          # Rating CRUD endpoints (/ratings)
│
├── templates/
│   ├── index.html          # Homepage with links to login and register
│   ├── login.html          # Login form
│   └── register.html       # Registration form
│
├── static/
│   ├── index.js            # Frontend JavaScript (fetch calls to the API)
│   └── styles.css          # Global stylesheet
│
└── data/
    ├── Books.csv           # ~270,000 book records (23.7 MB)
    ├── Users.csv           # ~278,000 user records (2.7 MB)
    └── Ratings.csv         # ~1,100,000 rating records (23.8 MB)
```

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│                 HTTP Client / Browser            │
└─────────────────────────┬───────────────────────┘
                          │
┌─────────────────────────▼───────────────────────┐
│               FastAPI Application (main.py)      │
│    - Mounts static files at /static              │
│    - Mounts Jinja2 templates at /templates       │
│    - Registers routers (users, books, ratings)   │
│    - Runs create_db_and_tables() on startup      │
└──────────┬──────────────┬────────────────────────┘
           │              │
┌──────────▼────┐  ┌──────▼──────────────────┐
│   Routers     │  │  serviceBooks.py         │
│  users.py     │  │  Google Books API client │
│  books.py     │  └──────────────────────────┘
│  ratings.py   │
└──────────┬────┘
           │
┌──────────▼────────────────────────────────────┐
│   SQLModel (models.py + schemas.py)            │
│   ORM models with Pydantic validation          │
└──────────┬─────────────────────────────────────┘
           │
┌──────────▼─────────────────────────────────────┐
│   SQLite (database.db)                          │
│   Populated on startup from CSV files via pandas│
└─────────────────────────────────────────────────┘
```
---

## Data Models

### User

| Field | Type | Constraints |
|---|---|---|
| User_ID | int | Primary key, auto-increment |
| username | str | Unique, indexed |
| password | str | bcrypt-hashed |

### Book

| Field | Type | Constraints |
|---|---|---|
| Book_ID | int | Primary key, auto-increment |
| ISBN | str | Unique identifier |
| Title | str | Required |
| Author | str | Nullable |
| Year | int | Nullable |
| Publisher | str | Nullable |

### Rating

| Field | Type | Constraints |
|---|---|---|
| User_ID | int | Foreign key → User.User_ID, composite PK |
| ISBN | str | Foreign key → Book.ISBN, composite PK |
| Rating | int | Numeric rating value |

Ratings have a composite primary key on `(User_ID, ISBN)`, enforcing that each user can rate each book only once. Foreign keys enforce referential integrity between all three tables.

---

## API Endpoints

### Users

| Method | Path | Description |
|---|---|---|
| POST | `/register` | Register a new user (hashes password with bcrypt) |
| POST | `/login` | Authenticate with username and password |
| GET | `/users` | List all users |
| GET | `/users/{user_id}` | Get a specific user by ID |
| GET | `/users/{user_id}/books` | Get all books rated by a user |
| PUT | `/users/{user_id}` | Update user information |
| DELETE | `/users/{user_id}` | Delete a user |

### Books

| Method | Path | Description |
|---|---|---|
| POST | `/books` | Create a new book record |
| GET | `/books` | List all books |
| GET | `/books/{id}` | Get a book by ID |
| GET | `/books/title/search?query=` | Case-insensitive title search (LIKE) |
| GET | `/books/author/search?author=` | Case-insensitive author search (LIKE) |
| GET | `/books/publisher/search?publisher=` | Case-insensitive publisher search (LIKE) |
| GET | `/import/title?title=` | Import books from Google Books API by title |
| PUT | `/books/{id}` | Update book information |
| DELETE | `/books/{book_ISBN}` | Delete a book by ISBN |

### Ratings

| Method | Path | Description |
|---|---|---|
| POST | `/ratings` | Submit a new rating |
| PUT | `/ratings/{user_id}/{book_ISBN}` | Update an existing rating |
| DELETE | `/ratings/{user_id}/{book_ISBN}` | Delete a rating |
| GET | `/books/{book_ISBN}/ratings` | Get all ratings for a book |

### Frontend

| Method | Path | Description |
|---|---|---|
| GET | `/` | Serves the HTML homepage via Jinja2 |

---

## External Integrations

### Google Books API

The `serviceBooks.py` module queries the Google Books API to fetch book metadata by title. The integration:

1. Sends a GET request to `https://www.googleapis.com/books/v1/volumes` with `intitle:{query}`
2. Parses up to 5 results from the response
3. Extracts ISBN (prefers ISBN-13 over ISBN-10), title, authors, published year, and publisher
4. Returns a list of structured book dictionaries ready for database insertion

This allows users to populate the database with real book data without manual entry, using the `GET /import/title?title=` endpoint.

A sample API response is included in `resposta.json` for reference.

---

## Frontend

The application includes a minimal browser-based frontend served directly by FastAPI:

- **Jinja2 templates** (`/templates`) render the homepage, login, and registration pages as server-side HTML
- **Static files** (`/static`) serve `index.js` (fetch-based API calls) and `styles.css`
- The JavaScript communicates with the FastAPI backend via `fetch()` calls to the REST endpoints

> **Note:** The frontend currently targets `http://127.0.0.1:8000` (hardcoded), so it only works in local development environments.

---

## Getting Started

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
git clone <repo-url>
cd API_biblioteca
pip install -r requirements.txt
```

### Running locally

```bash
uvicorn main:app --reload --port 8000
```

The app will be available at `http://127.0.0.1:8000`.

On first startup, the app will:
1. Create the SQLite database file (`database.db`)
2. Create all tables defined in `models.py`
3. Load `data/Books.csv`, `data/Users.csv`, and `data/Ratings.csv` into the database via pandas

---

## Running with Docker

### Build the image

```bash
docker build -t api-biblioteca .
```

### Run the container

```bash
docker run -p 8000:8000 api-biblioteca
```

The app will be accessible at `http://localhost:8000`.

The Dockerfile uses `python:3.11-slim` as the base image, installs dependencies from `requirements.txt`, copies the project files, and starts the server with Uvicorn bound to `0.0.0.0:8000`.

---


