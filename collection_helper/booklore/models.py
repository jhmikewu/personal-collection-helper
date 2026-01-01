"""Data models for Booklore responses."""

from typing import Optional, List
from pydantic import BaseModel, Field


class BookloreBook(BaseModel):
    """Represents a book in Booklore."""

    id: str
    title: str
    author: Optional[str] = None
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    publish_date: Optional[str] = None
    page_count: Optional[int] = Field(None, alias="pageCount")
    language: Optional[str] = None
    description: Optional[str] = None
    cover_url: Optional[str] = Field(None, alias="coverUrl")
    genres: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    rating: Optional[float] = None
    file_path: Optional[str] = Field(None, alias="filePath")

    class Config:
        """Pydantic config."""

        populate_by_name = True


class BookloreSeries(BaseModel):
    """Represents a book series in Booklore."""

    id: str
    name: str
    description: Optional[str] = None
    book_count: int = Field(alias="bookCount")

    class Config:
        """Pydantic config."""

        populate_by_name = True


class BookloreCollection(BaseModel):
    """Represents a collection in Booklore."""

    id: str
    name: str
    description: Optional[str] = None
    book_count: int = Field(alias="bookCount")

    class Config:
        """Pydantic config."""

        populate_by_name = True
