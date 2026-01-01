"""Data models for Emby API responses."""

from typing import Optional, List
from pydantic import BaseModel, Field


class EmbyMediaItem(BaseModel):
    """Represents a media item in Emby."""

    id: str = Field(alias="Id")
    name: str = Field(alias="Name")
    type: str = Field(alias="Type")
    media_type: Optional[str] = Field(None, alias="MediaType")
    premiere_date: Optional[str] = Field(None, alias="PremiereDate")
    production_year: Optional[int] = Field(None, alias="ProductionYear")
    community_rating: Optional[float] = Field(None, alias="CommunityRating")
    run_time_ticks: Optional[int] = Field(None, alias="RunTimeTicks")
    genres: List[str] = Field(default_factory=list, alias="Genres")
    studios: List[str] = Field(default_factory=list, alias="Studios")
    overview: Optional[str] = None

    class Config:
        """Pydantic config."""

        populate_by_name = True


class EmbyLibrary(BaseModel):
    """Represents a library in Emby."""

    id: str = Field(alias="Id")
    name: str = Field(alias="Name")
    type: str = Field(alias="Type")
    collection_type: Optional[str] = Field(None, alias="CollectionType")

    class Config:
        """Pydantic config."""

        populate_by_name = True


class EmbyUser(BaseModel):
    """Represents a user in Emby."""

    id: str = Field(alias="Id")
    name: str = Field(alias="Name")
    server_id: Optional[str] = Field(None, alias="ServerId")
    policy: Optional[dict] = None

    class Config:
        """Pydantic config."""

        populate_by_name = True
