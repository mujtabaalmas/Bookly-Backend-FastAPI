from fastapi import FastAPI, status
from src.books.routes import book_router
from src.auth.routes import auth_router
from src.reviews.routes import review_router
from contextlib import asynccontextmanager
from src.db.main import init_db
from .errors import (
    create_exception_handler,
    InvalidCredentials,
    #TagAlreadyExists,
    BookNotFound,
    UserAlreadyExists,
    UserNotFound,
    InsufficientPermission,
    AccessTokenRequired,
    InvalidToken,
    RefreshTokenRequired,
    RevokedToken,
    # BooklyException,
    # TagNotFound,
    # AccountNotVerified,
)


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
)

app.add_exception_handler(
    UserAlreadyExists,
    create_exception_handler(
        status_code=status.HTTP_403_FORBIDDEN,
        initial_detail={"message": "User with email already exists", "error_code": "user_exists"},
    ),
)
app.add_exception_handler(
    InvalidCredentials,
    create_exception_handler(
        status_code=status.HTTP_401_UNAUTHORIZED,
        initial_detail={"message": "Invalid Email or Password ", "error_code": "invalid_email_or_password"},
    ),
)

# app.add_exception_handler(
#     TagAlreadyExists,
#     create_exception_handler(
#         status_code=status.HTTP_403_FORBIDDEN,
#         initial_detail={"message": "user already exists", "error_code": "user_exists"},
#     ),
# )

app.add_exception_handler(
    BookNotFound,
    create_exception_handler(
        status_code=status.HTTP_404_NOT_FOUND,
        initial_detail={"message": "Book not found", "error_code": "book_not_found"},
    ),
)
app.add_exception_handler(
    UserNotFound,
    create_exception_handler(
        status_code=status.HTTP_404_NOT_FOUND,
        initial_detail={"message": "User not found with this email", "error_code": "user_not_found"},
    ),
)
app.add_exception_handler(
    InsufficientPermission,
    create_exception_handler(
        status_code=status.HTTP_401_UNAUTHORIZED,
        initial_detail={"message": "Not authorized", "error_code": "This user is not authorized for this resource"},
    ),
)
app.add_exception_handler(
    AccessTokenRequired,
    create_exception_handler(
        status_code=status.HTTP_401_UNAUTHORIZED,
        initial_detail={"message": "Please Provide valid Access token", "error_code": "access_token_required"},
    ),
)
app.add_exception_handler(
    InvalidToken,
    create_exception_handler(
        status_code=status.HTTP_401_UNAUTHORIZED,
        initial_detail={"message": "Access Token is Invalid ", "error_code": "invalid_token"},
    ),
)
app.add_exception_handler(
    RefreshTokenRequired,
    create_exception_handler(
        status_code=status.HTTP_403_FORBIDDEN,
        initial_detail={"message": "Please Provide valid Refresh token", "error_code": "refresh_token_required"},
    ),
)
app.add_exception_handler(
    RevokedToken,
    create_exception_handler(
        status_code=status.HTTP_401_UNAUTHORIZED,
        initial_detail={"message": "Token is invalid or has been revoked", "error_code": "token_revoked"},
    ),
)

app.include_router(book_router, prefix=f"/{api}/{version}/books", tags=["books"])
app.include_router(auth_router, prefix=f"/{api}/{version}/auth", tags=["auth"])
app.include_router(review_router, prefix=f"/{api}/{version}/reviews", tags=["reviews"])
