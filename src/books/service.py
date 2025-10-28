from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import BookCreateModel, BookUpdateModel
from sqlmodel import select, desc
from src.db.models import BookModel
from datetime import datetime
from fastapi import HTTPException, status
from src.errors import (
    BookNotFound
)
from uuid import UUID


class BookService:
    async def get_all_books(self, session: AsyncSession):

        statement = select(BookModel).order_by(desc(BookModel.created_at))
        result = await session.exec(statement)

        return result.all()

    async def get_user_books(self, user_uid: UUID, session: AsyncSession):

        statement = (
            select(BookModel)
            .where(BookModel.user_uid == user_uid)
            .order_by(desc(BookModel.created_at))
        )
        result = await session.exec(statement)

        return result.all()

    async def get_book(self, book_uid: UUID, session: AsyncSession):
        # Ensure we compare the model column to the UUID value (column == value)
        statement = select(BookModel).where(BookModel.uid == book_uid)
        result = await session.exec(statement)
        book = result.first()
        return book if book is not None else None

    async def get_book_by_title_and_author(self, title: str, author: str, session: AsyncSession):
        """Check if a book with the same title and author exists"""
        title = title.strip().upper()
        author = author.strip().upper()
        statement = select(BookModel).where(
            BookModel.title == title,
            BookModel.author == author
        )
        result = await session.exec(statement)
        return result.first()

    async def create_book(
        self, book_data: BookCreateModel, user_uid: UUID, session: AsyncSession
    ):

        title = book_data.title.strip().upper()
        author = book_data.author.strip().upper()
        publisher = book_data.publisher.strip().upper()

        result = await session.exec(
            select(BookModel).where(
                BookModel.title == title, BookModel.author == author
            )
        )
        existing_book = result.first()

        if existing_book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Book with same title '{book_data.title}', and author '{book_data.author}' already exists. Cannot Create ",
            )

        new_book = BookModel(
            title=title,
            author=author,
            publisher=publisher,
            page_count=book_data.page_count,
            published_date=book_data.published_date,
        )

        new_book.user_uid = user_uid

        session.add(new_book)
        await session.commit()
        await session.refresh(new_book)

        return new_book

    async def update_book(
        self, book_uid: UUID, update_data: BookUpdateModel, session: AsyncSession
    ):

        book_to_update = await self.get_book(book_uid, session)

        if book_to_update is not None:
            update_data_dict = update_data.model_dump()
            for k, v in update_data_dict.items():
                setattr(book_to_update, k, v)

            await session.commit()
            await session.refresh(book_to_update)
            return book_to_update
        else:
            return None

    async def delete_book(self, book_uid: UUID, session: AsyncSession):

        book_to_delete = await self.get_book(book_uid, session)
        if book_to_delete:
            await session.delete(book_to_delete)
            await session.commit()
            return {}
        else:
            return {"message": "book not found"}
