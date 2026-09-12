from database import Base

from sqlalchemy import String, SmallInteger, Integer, Table, ForeignKey, Column
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
