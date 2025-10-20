from fastapi import APIRouter, status, Header, HTTPException, Depends

# from src.books.books_data import books
from .schemas import BookModel, BookUpdateModel, BookCreateModel, BookDetailModel
from typing import Optional, List
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.service import BookService
from src.db.main import get_session
from src.auth.dependencies import AccessTokenBearer, RoleChecker

book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(["admin", "user"]))

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
@book_router.get("/", response_model=List[BookModel], dependencies=[role_checker])
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    # print("user detail that currently accessing resourse: ",token_details: dict)
    books = await book_service.get_all_books(session)
    return books


# USER BOOK DETAILS
@book_router.get(
    "/user/{user_uid}", response_model=List[BookModel], dependencies=[role_checker]
)
async def get_user_book_submission(
    user_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):

    books = await book_service.get_user_books(user_uid, session)
    if not books:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(f"books not found for user {user_uid} !!!"),
        )
    return books


# ROUTER TO CREATE BOOKS
@book_router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    response_model=BookModel,
    dependencies=[role_checker],
)
async def create_books(
    book_data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
) -> dict:
    """Router to create new book instance"""
    user_id = token_details.get("user")["user_uid"]
    new_book = await book_service.create_book(book_data, user_id, session)
    if not new_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=(f"book not created !!!")
        )
    # new_book = book_data.model_dump()
    # books.append(new_book)

    return new_book


# ROUTER TO GET BOOK BY ID
@book_router.get("/{book_uid}", response_model=BookDetailModel, dependencies=[role_checker])
async def get_book_by_id(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
) -> dict:
    """Router to get Book by books"""
    book = await book_service.get_book(book_uid, session)
    if book:
        return book
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="book not found"
        )


# ROUTER TO UPDATE BOOK
@book_router.patch(
    "/update/{book_uid}", response_model=BookModel, dependencies=[role_checker]
)
async def update_book(
    book_uid: str,
    book_update_data: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    """ROUTER TO UPDATE EXISTING BOOK BY BOOK ID"""

    updated_book = await book_service.update_book(book_uid, book_update_data, session)
    if updated_book:
        return updated_book
    else:

        # for book in books:
        #     if book['id'] == book_id:
        #         book['title'] = book_update_data.title
        #         book['author'] == book_update_data.author
        #         book['publisher'] = book_update_data.publisher
        #         book['page_count'] = book_update_data.page_count
        #         book['language'] = book_update_data.language
        #         # print(book_update_data) # for debugging purposes
        #         # print(book) # for debugging purposes only
        #         return book
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="book not found"
        )


# ROUTER TO DELETE BOOK BY ID
@book_router.delete(
    "/delete/{book_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[role_checker],
)
async def delete_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    """
    ROUTER TO DELETE EXISTING BOOK BY BOOK ID
    """
    book_to_delete = await book_service.delete_book(book_uid, session)
    if book_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="book id not found Unable to delete ",
        )
    else:
        return {}

    # for book in books:
    #     if book['id'] == book_id:
    #         books.remove(book)
    #         return {"message": "Item deleted"}
