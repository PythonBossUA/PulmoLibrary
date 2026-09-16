from database import Base

from sqlalchemy import String, SmallInteger, Integer, Table, ForeignKey, Column, Boolean, text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column


authors_books = Table(
    "authors_books",
    Base.metadata,
    Column("author_id", Integer, ForeignKey("authors.id"), primary_key=True),
    Column("book_id", Integer, ForeignKey("books.id"), primary_key=True),
)


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(127), nullable=False)
    year_of_writing: Mapped[int] = mapped_column(SmallInteger, nullable=False)


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(63), nullable=False)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(31), nullable=False)
    last_name: Mapped[str] = mapped_column(String(31), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(10), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(127), nullable=False)
    events_ok: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    sqlite_region_id: Mapped[int] = mapped_column(Integer, nullable=False)
    sqlite_settlement_id: Mapped[int] = mapped_column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "first_name",
            "last_name",
            "phone_number",
            "sqlite_region_id",
            "sqlite_settlement_id",
            name="unique_user"
        ),
    )