"""Unified data models for recommendations."""

from typing import Optional, List
from pydantic import BaseModel, Field


class UnifiedMediaItem(BaseModel):
    """Unified representation of a media item from Emby or Booklore."""

    id: str
    name: str
    source: str  # "emby" or "booklore"
    media_type: Optional[str] = None  # "movie", "series", "book", etc.
    authors: List[str] = Field(default_factory=list)
    year: Optional[int] = None
    genres: List[str] = Field(default_factory=list)
    description: Optional[str] = None


class RecommendationItem(BaseModel):
    """A recommended item with context."""

    name: str
    source: str
    media_type: Optional[str] = None
    reason: str  # Why this was recommended
    match_score: Optional[float] = None  # How well it matches (0-1)


class DailyRecommendations(BaseModel):
    """Daily recommendations response."""

    date: str
    recommendations: List[RecommendationItem]
    total_items_considered: int
    llm_provider: Optional[str] = None


class LLMConfig(BaseModel):
    """Configuration for LLM provider."""

    provider: str  # "openai", "anthropic", "ollama", etc.
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str
    max_tokens: int = 1000
    temperature: float = 0.7
