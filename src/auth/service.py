from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import UserCreateModel
from .utils import generate_password_hash, verify_password
from sqlmodel import select, desc
from src.db.models import User
from sqlalchemy.orm import selectinload
from datetime import datetime


class UserService:

    async def get_user_by_email(self, email: str, session: AsyncSession):

        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        user = result.first()
        return user

    async def user_exists(self, email, session: AsyncSession):

        user = await self.get_user_by_email(email, session)

        return True if user is not None else False

    async def create_user(self, user_data: UserCreateModel, session: AsyncSession):

        user_data_dict = user_data.model_dump()

        new_user = User(**user_data_dict)

        new_user.password_hash = generate_password_hash(user_data_dict["password"])
        new_user.role = "user"
        session.add(new_user)

        await session.commit()

        return new_user

    async def get_current_user_details(self, current_user: User, session: AsyncSession):
        result = await session.exec(
            select(User)
            .where(User.uid == current_user.uid)
            .options(
                selectinload(User.books),
                selectinload(User.reviews),
            )
        )
        user = result.scalar_one_or_none()
        if not user:
            return None
        else:
            user.reviews = [r for r in user.reviews if r.book_uid is not None]

            return user

    async def update_user(self, user: User, user_data: dict, session: AsyncSession):
        
        for k, v in user_data.items():
            setattr(user, k, v)

        await session.commit()
        
        return user