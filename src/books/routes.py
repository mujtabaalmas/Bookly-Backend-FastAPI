
from fastapi import APIRouter, status, Header, HTTPException
from src.books.books_data import books
from src.books.schemas import BookCreateModel, BookUpdateModel
from typing import Optional, List    

book_router  = APIRouter()

# ROUTER TO GET SELECTED HEADERS FROM API 
@book_router.get("/get_headers", status_code=status.HTTP_200_OK)
async def get_header(
    accept:str = Header(None),
    content_type : str = Header(None),
    user_agent : str = Header(None),
    host : str = Header(None),
    content_length : str = Header(None)
    ):

    request_Headers = {}
    request_Headers["Accept"] = accept
    request_Headers["Content-Type"] = content_type
    request_Headers["User_Agent"] = user_agent
    request_Headers["Host"] = host
    request_Headers["Content-Length"] = content_length

    # print(user_agent)
    return request_Headers

# ROUTER TO GET ALL BOOKS 
@book_router.get('/', response_model=List[BookCreateModel])
async def get_all_books():
    return books


# ROUTER TO CREATE BOOKS 
@book_router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_books(book_data : BookCreateModel) -> dict: 
    """Router to create new book instance"""
   
    newbook = book_data.model_dump()
    books.append(newbook) 
    if not newbook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=(f"book not created !!!"))
    return newbook


# ROUTER TO GET BOOK BY ID
@book_router.get('/{book_id}')
async def get_book_by_id(book_id : int) -> dict:
    """Router to get Book by books"""
    for book in books:
        if book['id'] == book_id:
            return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND ,detail="book not found")


#ROUTER TO UPDATE BOOK
@book_router.patch("/update/{book_id}")
async def update_book(book_id : int, book_update_data: BookUpdateModel) -> dict:
    """ROUTER TO UPDATE EXISTING BOOK BY BOOK ID """
    for book in books:
        if book['id'] == book_id:
            book['title'] = book_update_data.title
            book['author'] == book_update_data.author
            book['publisher'] = book_update_data.publisher
            book['page_count'] = book_update_data.page_count
            book['language'] = book_update_data.language
            # print(book_update_data) # for debugging purposes
            # print(book) # for debugging purposes only 
            return book
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="book not found")


# ROUTER TO DELETE BOOK BY ID 
@book_router.delete('/delete/{book_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id : int):
    """
    ROUTER TO DELETE EXISTING BOOK BY BOOK ID
    """
    for book in books:
        if book['id'] == book_id:
            books.remove(book)
            return {"message": "Item deleted"}
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="book id not found Unable to delete ")