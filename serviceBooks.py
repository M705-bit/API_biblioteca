import requests
import sys   

GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"

def fetch_books_by_title(title: str):
    params = {
        "q": f"intitle:{title}",
        "maxResults": 5
    }

    response = requests.get(GOOGLE_BOOKS_URL, params=params)
    response.raise_for_status()

    data = response.json()

    if "items" not in data:
        return []

    books = []
    for item in data["items"]:
        info = item["volumeInfo"]
        books.append({
            "ISBN": info.get("industryIdentifiers", [{}])[0].get("identifier"),
            "Title": info.get("title"),
            "Author": ", ".join(info.get("authors", [])),
            "Year": info.get("publishedDate", "")[:4],
            "Publisher": info.get("publisher")
        })

    return books

if __name__ == "__main__":
    title = " ".join(sys.argv[1:])
    data = fetch_books_by_title(title)
    print(data)