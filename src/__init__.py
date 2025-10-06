from fastapi import FastAPI
from src.books.routes import book_router

version = "v1"
api_key = "api"
api = api_key

app = FastAPI(
    title="Brookly App",
    description="A Rest Api for book review web service",
    version= version
)

app.include_router(book_router, prefix=f"/{api}/{version}/books", tags=['books'])