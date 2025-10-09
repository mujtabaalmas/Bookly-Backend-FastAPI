from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import BookCreateModel, BookUpdateModel
from sqlmodel import select, desc
from .models import BookModel
from datetime import datetime
from fastapi import HTTPException, status


class BookService:
    async def get_all_books(self, session: AsyncSession):

        statement = select(BookModel).order_by(desc(BookModel.created_at))
        result = await session.exec(statement)

        return result.all()

    async def get_book(self, book_uid: str, session: AsyncSession):

        statement = select(BookModel).where(book_uid == BookModel.uid)
        result = await session.exec(statement)

        book = result.first()
        return book if book is not None else None

    async def create_book(self, book_data: BookCreateModel, session: AsyncSession):

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

        session.add(new_book)
        await session.commit()
        await session.refresh(new_book)

        return new_book

    async def update_book(
        self, book_uid: str, update_data: BookUpdateModel, session: AsyncSession
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

        # statement = select(BookModel).where(book_uid == book_uid)

        # result = await session.exec(statement)
        # data_to_be_updated = update_data.model_dump()
        # update_data = BookModel(**data_to_be_updated)
        # session.add(update_data)
        # await session.commit()

        # return update_data

    async def delete_book(self, book_uid: str, session: AsyncSession):

        book_to_delete = await self.get_book(book_uid, session)
        if book_to_delete:
            await session.delete(book_to_delete)
            await session.commit()
            return {}
        else:
            return {"message": "book not found"}
