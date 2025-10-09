from sqlmodel import SQLModel, Field, Column
import sqlalchemy as pg
import uuid
from datetime import datetime


class User(SQLModel, table=True):
    __tablename__ = "users"

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )

    username: str = Field(sa_column=Column(pg.String(100), nullable=False))
    password_hash: str = Field(exclude=True)

    email: str = Field(sa_column=Column(pg.String(100), nullable=False))

    first_name: str = Field(sa_column=Column(pg.String(100), nullable=False))
    last_name: str = Field(sa_column=Column(pg.String(100), nullable=False))

    is_verified: bool = Field(default=False)

    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now())
    )

    def __repr__(self):
        return f"User {self.username}"
