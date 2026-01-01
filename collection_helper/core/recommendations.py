"""Recommendation engine."""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from collection_helper.core.manager import MediaManager
from collection_helper.core.llm_client import LLMClient
from collection_helper.core.models import (
    UnifiedMediaItem,
    RecommendationItem,
    DailyRecommendations,
    LLMConfig,
)
from collection_helper.logger import get_logger

logger = get_logger()


class RecommendationEngine:
    """Engine for generating media recommendations."""

    def __init__(self, llm_config: LLMConfig):
        """Initialize the recommendation engine.

        Args:
            llm_config: LLM configuration
        """
        self.llm_config = llm_config

    async def generate_daily_recommendations(
        self,
        count: int = 5,
        user_preferences: Optional[str] = None,
    ) -> DailyRecommendations:
        """Generate daily recommendations from the collection.

        Generates separate recommendations for books and videos:
        - N recommendations based on collection patterns (genres, authors, themes)
        - 1 surprise recommendation per category to diversify the collection
        Total: (N + 1) recommendations per category

        Args:
            count: Number of pattern-based recommendations to generate PER CATEGORY (books and videos)
            user_preferences: Optional user preferences/context

        Returns:
            Daily recommendations including both pattern-based and surprise recommendations
        """
        logger.info("Generating daily recommendations")

        # Fetch all items from both sources
        unified_items = await self._fetch_and_clean_items()

        logger.info(f"Fetched and cleaned {len(unified_items)} items")

        # Separate items by category
        book_items = [item for item in unified_items if item.source == "booklore"]
        video_items = [item for item in unified_items if item.source == "emby"]

        logger.info(f"Found {len(book_items)} books and {len(video_items)} videos")

        # Generate recommendations using LLM
        llm_client = LLMClient(self.llm_config)
        recommendations = []

        try:
            # Generate book recommendations
            if book_items:
                logger.info("Generating book recommendations")
                books_dict = [item.model_dump() for item in book_items]
                book_response = await llm_client.generate_recommendations(
                    items=books_dict,
                    count=count,
                    user_preferences=user_preferences,
                    category="book",
                    include_surprise=True,
                )
                book_recommendations = self._parse_llm_response(book_response, book_items, category="book")
                recommendations.extend(book_recommendations)
                logger.info(f"Generated {len(book_recommendations)} book recommendations")

            # Generate video recommendations
            if video_items:
                logger.info("Generating video recommendations")
                videos_dict = [item.model_dump() for item in video_items]
                video_response = await llm_client.generate_recommendations(
                    items=videos_dict,
                    count=count,
                    user_preferences=user_preferences,
                    category="video",
                    include_surprise=True,
                )
                video_recommendations = self._parse_llm_response(video_response, video_items, category="video")
                recommendations.extend(video_recommendations)
                logger.info(f"Generated {len(video_recommendations)} video recommendations")

            return DailyRecommendations(
                date=datetime.now().isoformat(),
                recommendations=recommendations,
                total_items_considered=len(unified_items),
                llm_provider=self.llm_config.provider,
            )
        finally:
            await llm_client.close()

    async def _fetch_and_clean_items(self) -> List[UnifiedMediaItem]:
        """Fetch items from Emby and Booklore and convert to unified format.

        Returns:
            List of unified media items
        """
        items = []

        async with MediaManager() as manager:
            # Fetch from Emby
            try:
                emby_items = await manager.get_emby_items(limit=1000)
                for item in emby_items:
                    unified = UnifiedMediaItem(
                        id=f"emby_{item.id}",
                        name=item.name,
                        source="emby",
                        media_type=item.media_type or item.type.lower(),
                        authors=[],  # Emby items don't typically have authors
                        year=item.production_year,
                        genres=item.genres,
                        description=item.overview,
                    )
                    items.append(unified)
                logger.info(f"Fetched {len(emby_items)} items from Emby")
            except Exception as e:
                logger.error(f"Failed to fetch Emby items: {e}")

            # Fetch from Booklore
            try:
                booklore_books = await manager.get_booklore_books(limit=1000)
                for book in booklore_books:
                    unified = UnifiedMediaItem(
                        id=f"booklore_{book.id}",
                        name=book.title,
                        source="booklore",
                        media_type="book",
                        authors=book.authors,
                        year=None,  # Booklore doesn't provide year in main fields
                        genres=book.categories,
                        description=book.description,
                    )
                    items.append(unified)
                logger.info(f"Fetched {len(booklore_books)} books from Booklore")
            except Exception as e:
                logger.error(f"Failed to fetch Booklore books: {e}")

        return items

    def _parse_llm_response(
        self,
        llm_response: str,
        available_items: List[UnifiedMediaItem],
        category: str = "mixed",
    ) -> List[RecommendationItem]:
        """Parse the LLM response into recommendation items.

        Args:
            llm_response: Raw response from LLM
            available_items: List of items in the user's collection (for analysis)
            category: The category of recommendations ("book", "video", or "mixed")

        Returns:
            List of recommendation items (suggested new items)
        """
        try:
            # Try to extract JSON from the response
            # LLMs sometimes add text around the JSON
            start_idx = llm_response.find("{")
            end_idx = llm_response.rfind("}") + 1

            if start_idx == -1 or end_idx == -1:
                logger.warning("No JSON found in LLM response")
                return []

            json_str = llm_response[start_idx:end_idx]
            data = json.loads(json_str)

            recommendations = []
            for rec in data.get("recommendations", []):
                name = rec.get("name", "")
                reason = rec.get("reason", "")

                # Use category to determine media type directly
                # No keyword guessing needed since we know the category from the LLM call
                if category == "book":
                    media_type = "book"
                    source = "suggested_book"
                elif category == "video":
                    media_type = "video"
                    source = "suggested_video"
                else:
                    # For mixed mode, fall back to keyword detection
                    reason_lower = reason.lower()
                    if any(keyword in reason_lower for keyword in ["book", "novel", "author", "read", "reading"]):
                        media_type = "book"
                        source = "suggested_book"
                    elif any(keyword in reason_lower for keyword in ["movie", "film", "watch", "series", "show"]):
                        media_type = "video"
                        source = "suggested_video"
                    else:
                        # Default to video if unclear
                        media_type = "video"
                        source = "suggested_video"

                recommendations.append(
                    RecommendationItem(
                        name=name,
                        source=source,
                        media_type=media_type,
                        reason=reason,
                        match_score=rec.get("match_score"),
                    )
                )

            return recommendations
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.debug(f"LLM response was: {llm_response}")
            return []
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return []
