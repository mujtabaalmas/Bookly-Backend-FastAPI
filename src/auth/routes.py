from fastapi import APIRouter, Depends, HTTPException, status
from .schemas import (
    UserCreateModel,
    UserModel,
    UserloginModel,
    UserBooksModel,
    EmailModel,
    PasswordResetRequestModel,
    PasswordResetConfirmModel,
)
from .service import UserService
from src.db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from .utils import (
    create_access_token,
    decode_token,
    generate_password_hash,
    verify_password,
    create_url_safe_token,
    decode_url_safe_token,
)
from fastapi.responses import JSONResponse
from datetime import timedelta, datetime
from .dependencies import (
    RefreshTokenBearer,
    AccessTokenBearer,
    get_current_user,
    RoleChecker,
)
from src.db.redis import add_jti_to_blocklist
from src.config import Config
from src.db.main import get_session
from src.errors import (
    InvalidToken,
    UserAlreadyExists,
    InvalidCredentials,
    UserNotFound,
)
from src.mail import mail, create_message, send_verification_email

auth_router = APIRouter()
user_service = UserService()
role_checker = RoleChecker(["admin", "user"])

REFRESH_TOKEN_EXPIRY = 1


@auth_router.post("/send_mail")
async def send_mail(emails: EmailModel):
    emails = emails.addresses
    html = """<h1>welcome to the app bookly</h1> 
            <h2>Email sent from FastAPI API testing only</h2>"""
    message = create_message(recipients=emails, subject="Welcome", body=html)

    await mail.send_message(message)

    return {"message": "Email sent successfully"}


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def create_user_Account(
    user_data: UserCreateModel, session: AsyncSession = Depends(get_session)
):
    email = user_data.email

    User_exists = await user_service.user_exists(email, session)

    if User_exists:
        raise UserAlreadyExists()

    new_user = await user_service.create_user(user_data, session)
    token = create_url_safe_token({"email": email})
    Link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{token}"

    # Send templated email
    await send_verification_email(
        email=email, username=user_data.username, verify_link=Link
    )

    return {
        "message": "Account Created Successfully! Check your email to verify your account.",
        "user": new_user,
    }

    # Below is Simple sending text with link to email

    # html_message = f"""
    #     <h1>Please verify your email</h1>
    #     <p>Click on this <a href="{Link}">Link</a> to verify your account</p>
    # """
    # message = create_message(
    #     recipients=[email], subject="Verify Your Bookly Account", body=html_message
    # )
    # await mail.send_message(message)

    # return {
    #     "message": "Account Created Successfully! Check Email to verify your account",
    #     "user": new_user,
    # }

    # return new_user


@auth_router.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):

    token_data = decode_url_safe_token(token)
    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFound()
        await user_service.update_user(user, {"is_verified": True}, session)

        return JSONResponse(
            content={"message": "Account Verified succesfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "something went wrong cannot verify your account"},
        status_code=status.HTTP_502_BAD_GATEWAY,
    )


@auth_router.post("/login")
async def login_users(
    user_login_data: UserloginModel, session: AsyncSession = Depends(get_session)
):
    email = user_login_data.email
    password = user_login_data.password

    user = await user_service.get_user_by_email(email, session)

    if user is not None:
        password_valid = verify_password(password, user.password_hash)

        if password_valid:
            access_token = create_access_token(
                user_data={
                    "email": user.email,
                    "user_uid": str(user.uid),
                    "role": user.role,
                }
            )
            # else:
            #     print("meoe pass incorect")

            refresh_token = create_access_token(
                user_data={"email": user.email, "user_uid": str(user.uid)},
                refresh=True,
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
            )

            return JSONResponse(
                content={
                    "message": "Login succesfull",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {"email": user.email, "user_uid": str(user.uid)},
                    "token_type": "bearer",
                }
            )
    raise InvalidCredentials()
    # raise HTTPException(
    #     status_code=status.HTTP_403_FORBIDDEN,
    #     detail="Invalid Credentials Please try again",
    # )


@auth_router.get("/refresh_token")
async def get_new_access_token(token_details: dict = Depends(RefreshTokenBearer())):
    expiry_timestamp = token_details["exp"]
    if datetime.fromtimestamp(expiry_timestamp) > datetime.now():
        new_acces_token = create_access_token(user_data=token_details["user"])
        return JSONResponse(content={"new_access_token": new_acces_token})

    raise InvalidToken()
    # raise HTTPException(
    #     status_code=status.HTTP_400_BAD_REQUEST, detail="invalid or expired token"
    # )


@auth_router.get("/me", response_model=UserBooksModel)
async def get_current_user(
    user=Depends(get_current_user), _: bool = Depends(role_checker)
):
    if user is None:
        raise UserNotFound()
    return user


@auth_router.get("/logout")
async def revoke_token(token_details: dict = Depends(AccessTokenBearer())):

    jti = token_details["jti"]

    await add_jti_to_blocklist(jti)

    return JSONResponse(
        content={"message": "logged out succesfully"}, status_code=status.HTTP_200_OK
    )


@auth_router.post("/password-reset-request")
async def password_reset_request(email_data: PasswordResetRequestModel):

    email = email_data.email
    token = create_url_safe_token({"email": email})
    Link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{token}"

    html_message = f"""
        <h1>Reset your password</h1>
        <p>Click on this <a href="{Link}">Link</a> to Reset your Password</p>
    """
    message = create_message(
        recipients=[email], subject="Reset Your Password", body=html_message
    )

    await mail.send_message(message)
    return JSONResponse(
        content={
            "message": "Please check your email for password reset link",
        },
        status_code=status.HTTP_200_OK,
    )


@auth_router.post("/password-reset-confirm/{token}")
async def reset_account_password(
    token: str,
    passwords: PasswordResetConfirmModel,
    session: AsyncSession = Depends(get_session),
):
    new_passie = passwords.new_password
    confirm_new_passie = passwords.confirm_new_password

    if new_passie != confirm_new_passie:
        raise HTTPException(
            detail={
                "message": "Passwords do not match",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    token_data = decode_url_safe_token(token)

    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)
        if not user:
            raise UserNotFound()

        password_hash = generate_password_hash(new_passie)
        await user_service.update_user(user, {"password_hash": password_hash}, session)

        return JSONResponse(
            content={
                "message": "Password reset successfully ",
            },
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={
            "message": "AN error occured while reseting your passowrd",
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
