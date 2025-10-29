from fastapi import APIRouter, Depends, HTTPException, status
from src.db.models import User
from src.db.main import get_session
from src.auth.dependencies import get_current_user
from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import ReviewCreateModel, ReviewModel
from .service import ReviewService
from uuid import UUID

review_service = ReviewService()
review_router = APIRouter()


@review_router.post(
    "/{book_uid}",
    responses={
        200: {"description": "Review added successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "Book not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
async def add_review_to_books(
    book_uid: UUID,
    review_data: ReviewCreateModel,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    new_review = await review_service.add_review_to_book(
        user_email=current_user.email,
        review_data=review_data,
        book_uid=book_uid,
        session=session,
    )

    return new_review