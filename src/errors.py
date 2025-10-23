from typing import Any, Callable
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi import FastAPI, status


class BooklyException(Exception):
    """This is the base class for all bookly errors"""

    pass


class InvalidToken(BooklyException):
    """User has provided an invalid or expired token"""

    pass


class RevokedToken(BooklyException):
    """User has provided a token that has been revoked"""

    pass


class AccessTokenRequired(BooklyException):
    """User has provided a refresh token when an access token is needed"""

    pass


class RefreshTokenRequired(BooklyException):
    """User has provided an access token when a refresh token is needed"""

    pass


class UserAlreadyExists(BooklyException):
    """User has provided an email for a user who exists during sign up."""

    pass


class InvalidCredentials(BooklyException):
    """User has provided wrong email or password during log in."""

    pass


class InsufficientPermission(BooklyException):
    """User does not have the neccessary permissions to perform an action."""

    pass


class BookNotFound(BooklyException):
    """Book Not found"""

    pass


class TagNotFound(BooklyException):
    """Tag Not found"""

    pass


class TagAlreadyExists(BooklyException):
    """Tag already exists"""

    pass


class UserNotFound(BooklyException):
    """User Not found"""

    pass


class AccountNotVerified(Exception):
    """Account not yet verified"""

    pass


def create_exception_handler(
    status_code: int, initial_detail: Any
) -> Callable[[Request, Exception], JSONResponse]:

    async def exception_handler(request: Request, exc: BooklyException):
        return JSONResponse(content=initial_detail, status_code=status_code)

    return exception_handler


def register_all_errors(app: FastAPI):

    app.add_exception_handler(
        UserAlreadyExists,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "User with email already exists",
                "error_code": "user_exists",
            },
        ),
    )
    app.add_exception_handler(
        InvalidCredentials,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Invalid Email or Password ",
                "error_code": "invalid_email_or_password",
            },
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
            initial_detail={
                "message": "Book not found",
                "error_code": "book_not_found",
            },
        ),
    )
    app.add_exception_handler(
        UserNotFound,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "User not found with this email",
                "error_code": "user_not_found",
            },
        ),
    )
    app.add_exception_handler(
        InsufficientPermission,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Not authorized",
                "error_code": "This user is not authorized for this resource",
            },
        ),
    )
    app.add_exception_handler(
        AccessTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Please Provide valid Access token",
                "error_code": "access_token_required",
            },
        ),
    )
    app.add_exception_handler(
        InvalidToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Access Token is Invalid ",
                "error_code": "invalid_token",
            },
        ),
    )
    app.add_exception_handler(
        RefreshTokenRequired,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Please Provide valid Refresh token",
                "error_code": "refresh_token_required",
            },
        ),
    )
    app.add_exception_handler(
        RevokedToken,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Token is invalid or has been revoked",
                "error_code": "token_revoked",
            },
        ),
    )

    @app.exception_handler(500)
    async def internal_server_error(request, exc):
        return JSONResponse(
            content={
                "message": "Oops ! Something went wrong hehe",
                "error_code": "server_error",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
