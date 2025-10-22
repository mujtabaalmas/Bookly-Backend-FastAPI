from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy as pg
from src.books.schemas import BookModel
from typing import Optional, List
import uuid
from datetime import datetime, date


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
    role: str = Field(
        sa_column=Column(pg.VARCHAR, nullable=False, server_default="user")
    )
    is_verified: bool = Field(default=False)

    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now())
    )
    updated_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now())
    )
    books: List["BookModel"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
        },
    )
    reviews: List["Review"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
        },
    )

    def __repr__(self):
        return f"User {self.username}"


from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy as pg
from datetime import datetime, date
from typing import Optional
from sqlalchemy import ForeignKey
import uuid


class BookModel(SQLModel, table=True):
    __tablename__ = "books"

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )

    title: str = Field(sa_column=Column(pg.String(150), nullable=False))
    author: str = Field(sa_column=Column(pg.String(150), nullable=False))
    publisher: str = Field(sa_column=Column(pg.String(150), nullable=False))
    published_date: date
    page_count: int = Field(sa_column=Column(pg.INTEGER(), nullable=False))
    language: str = Field(sa_column=Column(pg.String(100), default="English"))
    user_uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("users.uid", ondelete="CASCADE"),  # ✅ ensure cascade from User → Books
            nullable=False,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now())
    )
    update_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now())
    )
    user: Optional["User"] = Relationship(back_populates="books")
    reviews: List["Review"] = Relationship(
        back_populates="books",
        sa_relationship_kwargs={
            "lazy": "selectin",
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
        },
    )

    def __repr__(self):
        return f"<Book {self.title}>"


class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    ratings: int = Field(ge=1, le=5)
    review_text: str
    user_uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("users.uid", ondelete="CASCADE"),
            nullable=False,
        )
    )
    book_uid: uuid.UUID = Field(
        sa_column=Column(
            pg.UUID(as_uuid=True),
            ForeignKey("books.uid", ondelete="CASCADE"),
            nullable=False,
        )
    )
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now())
    )
    update_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now())
    )
    user: Optional[User] = Relationship(back_populates="reviews")
    books: Optional[BookModel] = Relationship(back_populates="reviews")

    def __repr__(self):
        return f"<Review for {self.book_uid} by user {self.user_uid}>"
