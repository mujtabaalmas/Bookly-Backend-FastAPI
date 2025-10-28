from src.db.models import Review
from src.auth.service import UserService
from src.books.service import BookService
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status
from .schemas import ReviewCreateModel
from sqlmodel import select, desc
from uuid import UUID
import datetime
import logging

book_service = BookService()
user_service = UserService()


class ReviewService:

    async def add_review_to_book(
        self,
        user_email: str,
        book_uid: UUID,
        review_data: ReviewCreateModel,
        session: AsyncSession,
    ):
        try:
            book = await book_service.get_book(book_uid=book_uid, session=session)
            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Book not found cannot add review",
                )
            user = await user_service.get_user_by_email(
                email=user_email, session=session
            )
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found cannot add review",
                )

            statement = select(Review).where(
                Review.book_uid == book.uid, Review.user_uid == user.uid
            )

            result = await session.exec(statement)
            existing_review = result.first()
            if existing_review:
                existing_review.ratings = review_data.ratings
                existing_review.review_text = review_data.review_text
                existing_review.update_at = datetime.datetime.now()
                await session.commit()

                return existing_review
            else:
                review_data_dict = review_data.model_dump()

                new_review = Review(user=user, books=book, **review_data_dict)

                session.add(new_review)
                await session.commit()

                return new_review

        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Oops  ... something went wrong",
            )
