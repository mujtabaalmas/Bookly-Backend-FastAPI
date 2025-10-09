from fastapi import FastAPI
from src.books.routes import book_router
from src.auth.routes import auth_router
from contextlib import asynccontextmanager
from src.db.main import init_db


@asynccontextmanager
async def life_span(app: FastAPI):
    print(f"server is starting . . .")
    await init_db()
    yield
    print(f"server has been stopped")


version = "v1"
api_key = "api"
api = api_key

app = FastAPI(
    title="Brookly App",
    description="A Rest Api for book review web service",
    version=version,
    lifespan=life_span,
)

app.include_router(book_router, prefix=f"/{api}/{version}/books", tags=["books"])
app.include_router(auth_router, prefix=f"/{api}/{version}/auth", tags=["auth"])
