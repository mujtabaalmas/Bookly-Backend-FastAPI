from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import BookCreateModel, BookUpdateModel
from sqlmodel import select, desc
from .models import BookModel
from datetime import datetime

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
        book_data_dict = book_data.model_dump()
        new_book = BookModel(**book_data_dict)
        new_book.published_date = book_data_dict['published_date']
        # new_book.published_date = datetime.strptime(book_data_dict['published_date'],"%Y-%m-%d")
        session.add(new_book)
        await session.commit()

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
        
