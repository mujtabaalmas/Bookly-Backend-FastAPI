from fastapi import APIRouter, status, Header, HTTPException, Depends

# from src.books.books_data import books
from .schemas import BookModel, BookUpdateModel, BookCreateModel, BookDetailModel
from typing import Optional, List
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.service import BookService
from src.db.main import get_session
from src.auth.dependencies import AccessTokenBearer, RoleChecker

book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(["admin", "user"]))
from src.errors import BookNotFound

# ROUTER TO GET SELECTED HEADERS FROM API
# @book_router.get("/get_headers", status_code=status.HTTP_200_OK)
# async def get_header(
#     accept:str = Header(None),
#     content_type : str = Header(None),
#     user_agent : str = Header(None),
#     host : str = Header(None),
#     content_length : str = Header(None),
#     session:AsyncSession = Depends(get_session)
#     ):

#     request_Headers = {}
#     request_Headers["Accept"] = accept
#     request_Headers["Content-Type"] = content_type
#     request_Headers["User_Agent"] = user_agent
#     request_Headers["Host"] = host
#     request_Headers["Content-Length"] = content_length

#     # print(user_agent)
#     return request_Headers


# ROUTER TO GET ALL BOOKS
@book_router.get(
    "/",
    response_model=List[BookModel],
    dependencies=[role_checker],
    responses={
        200: {"description": "List of all books"},
        400: {"description": "Bad Request - Invalid input"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
    }
)
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    books = await book_service.get_all_books(session)
    return books


# USER BOOK DETAILS
@book_router.get(
    "/user/{user_uid}", 
    response_model=List[BookModel], 
    dependencies=[role_checker],
    responses={
        200: {"description": "List of user's books"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "User or books not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_user_book_submission(
    user_uid: UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    try:
        books = await book_service.get_user_books(user_uid, session)
        if not books:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No books found for this user"
            )
        return books
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ROUTER TO CREATE BOOKS
@book_router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=BookModel,
    dependencies=[role_checker],
    responses={
        201: {"description": "Book created successfully"},
        400: {"description": "Book with same title and author already exists"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)
async def create_books(
    book_data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
) -> dict:
    """Router to create new book instance"""
    try:
        user_id = token_details.get("user")["user_uid"]
        
        # Check if book with same title and author exists
        existing_book = await book_service.get_book_by_title_and_author(
            book_data.title, book_data.author, session
        )
        if existing_book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Book with same title '{book_data.title}', and author '{book_data.author}' already exists. Cannot Create"
            )
            
        new_book = await book_service.create_book(book_data, user_id, session)
        if not new_book:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create book"
            )
        return new_book
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Explicitly return 405 for unsupported GET on "/create" to avoid UUID route conflict
@book_router.get("/create")
async def create_books_method_not_allowed():
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="Method Not Allowed"
    )


# ROUTER TO GET BOOK BY ID
@book_router.get(
    "/{book_uid}", 
    response_model=BookDetailModel, 
    dependencies=[role_checker],
    responses={
        200: {"description": "Book details retrieved successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "Book not found"},
        500: {"description": "Internal server error"}
    }
)
async def get_book_by_id(
    book_uid: UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
) -> dict:
    """Router to get Book by ID"""
    try:
        book = await book_service.get_book(book_uid, session)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )
        return book
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ROUTER TO UPDATE BOOK
@book_router.patch(
    "/update/{book_uid}",
    response_model=BookModel,
    dependencies=[role_checker],
    responses={
        200: {"description": "Book updated successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "Book not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
async def update_book(
    book_uid: UUID,
    book_update_data: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    """ROUTER TO UPDATE EXISTING BOOK BY BOOK ID"""

    updated_book = await book_service.update_book(book_uid, book_update_data, session)

    if updated_book is None:
        raise BookNotFound()
    else:
        return updated_book
        # raise HTTPException(
        #     status_code=status.HTTP_404_NOT_FOUND, detail="book not found"
        # )


# ROUTER TO DELETE BOOK BY ID
@book_router.delete(
    "/delete/{book_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[role_checker],
    responses={
        204: {"description": "Book deleted successfully"},
        401: {"description": "Not authenticated"},
        403: {"description": "Insufficient permissions"},
        404: {"description": "Book not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
async def delete_book(
    book_uid: UUID,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    """
    ROUTER TO DELETE EXISTING BOOK BY BOOK ID
    """
    result = await book_service.delete_book(book_uid, session)
    if isinstance(result, dict) and result.get("message") == "book not found":
        raise BookNotFound()
    return {}
