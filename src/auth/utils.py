from passlib.context import CryptContext
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer
from src.config import Config
import jwt
import uuid
import logging

password_context = CryptContext(schemes=["bcrypt"])

ACCESS_TOKEN_EXPIRY = 3600


def generate_password_hash(password: str) -> str:

    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]  
    return password_context.hash(password_bytes)


def verify_password(password: str, hash: str) -> bool:
    return password_context.verify(password, hash)


def create_access_token(
    user_data: dict, expiry: timedelta = None, refresh: bool = False
):
    payload = {}

    payload["user"] = user_data
    payload["exp"] = datetime.now() + (
        expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY)
    )
    payload["jti"] = str(uuid.uuid4())

    payload["refresh"] = refresh

    token = jwt.encode(
        payload=payload, key=Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM
    )

    return token


def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token, key=Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM]
        )
        return token_data
    except jwt.PyJWKError as e:
        logging.exception(e)
        return None


our_token_serializer = URLSafeTimedSerializer(
    secret_key=Config.JWT_SECRET, salt="o-mera-nam-a-khokhar"
)


def create_url_safe_token(data: dict):

    token = our_token_serializer.dumps(data)

    return token


def decode_url_safe_token(token: str):

    try:
        token_data = our_token_serializer.loads(token)
        return token_data
    except Exception as e:
        logging.error(str(e))
