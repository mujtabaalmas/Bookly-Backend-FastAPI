# from sqlmodel import create_engine, text, SQLModel
# from sqlalchemy.ext.asyncio import AsyncEngine
# from sqlmodel.ext.asyncio.session import AsyncSession
# from sqlalchemy.orm import sessionmaker
# from src.books.models import BookModel

# from src.config import Config

# engine = AsyncEngine(
#     create_engine(
#     url=Config.DATABASE_URL,
#     echo=True
# ))

# async def init_db():
#     async with engine.begin() as conn:
#         # statement = text("SELECT 'hello';")
#         # result = await conn.execute(statement)
#         # print(result.all())

#         await conn.run_sync(SQLModel.metadata.create_all)


# async def get_session() -> AsyncSession:

#     Session = sessionmaker(
#         bind=AsyncEngine,
#         class_=AsyncSession,
#         expire_on_commit=False
#     )

#     async with Session() as session:
#         yield session

# src/db.py

from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.config import Config


#  Create proper async engine
engine = create_async_engine(
    Config.DATABASE_URL,  # e.g., "postgresql+asyncpg://user:pass@localhost/dbname"
    echo=True,
)


#  Create async session factory
SessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


#  Initialize database tables
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


# Dependency for FastAPI routes
async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
