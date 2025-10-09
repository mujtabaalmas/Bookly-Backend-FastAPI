from sqlmodel import SQLModel, Field, Column
import sqlalchemy as pg
from datetime import datetime, date
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
    created_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now())
    )
    update_at: datetime = Field(
        sa_column=Column(pg.TIMESTAMP(timezone=True), default=datetime.now())
    )

    def __repr__(self):
        return f"Book {self.title}"
