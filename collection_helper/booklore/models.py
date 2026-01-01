"""Data models for Booklore responses."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator


class BookloreMetadata(BaseModel):
    """Booklore book metadata."""

    title: str
    authors: List[str] = Field(default_factory=list)
    publisher: Optional[str] = None
    publishedDate: Optional[str] = None
    pageCount: Optional[int] = None
    language: Optional[str] = None
    description: Optional[str] = None
    isbn13: Optional[str] = None
    categories: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    seriesName: Optional[str] = None


class BookloreBook(BaseModel):
    """Represents a book in Booklore."""

    id: int  # Booklore returns integer IDs
    title: str = ""
    authors: List[str] = Field(default_factory=list)
    publisher: Optional[str] = None
    publish_date: Optional[str] = None
    page_count: Optional[int] = None
    language: Optional[str] = None
    description: Optional[str] = None
    isbn13: Optional[str] = None
    categories: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    series_name: Optional[str] = None
    book_type: Optional[str] = Field(None, alias="bookType")
    library_name: Optional[str] = Field(None, alias="libraryName")
    file_name: Optional[str] = Field(None, alias="fileName")
    file_size_kb: Optional[int] = Field(None, alias="fileSizeKb")
    added_on: Optional[str] = Field(None, alias="addedOn")
    metadata: Optional[Dict[str, Any]] = None

    @field_validator('title', 'authors', 'publisher', 'publish_date', 'page_count',
                     'language', 'description', 'isbn13', 'categories', 'tags', 'series_name', mode='before')
    @classmethod
    def extract_from_metadata(cls, v, info):
        """Extract fields from nested metadata object."""
        if isinstance(v, dict) or v is None:
            # Get the raw data
            raw_data = info.data.get('metadata', {})
            if isinstance(raw_data, dict):
                field_name = info.field_name
                if field_name == 'publish_date':
                    return raw_data.get('publishedDate')
                elif field_name == 'page_count':
                    return raw_data.get('pageCount')
                elif field_name == 'series_name':
                    return raw_data.get('seriesName')
                elif field_name in raw_data:
                    return raw_data.get(field_name)
        return v

    class Config:
        """Pydantic config."""

        populate_by_name = True


class BookloreSeries(BaseModel):
    """Represents a book series in Booklore."""

    id: int  # Booklore returns integer IDs
    name: str
    description: Optional[str] = None
    book_count: int = Field(default=0, alias="bookCount")

    class Config:
        """Pydantic config."""

        populate_by_name = True


class BookloreCollection(BaseModel):
    """Represents a collection in Booklore."""

    id: int  # Booklore returns integer IDs
    name: str
    description: Optional[str] = None
    book_count: int = Field(default=0, alias="bookCount")

    class Config:
        """Pydantic config."""

        populate_by_name = True
