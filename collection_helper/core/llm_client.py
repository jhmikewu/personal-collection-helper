"""LLM client for generating recommendations."""

from typing import List, Optional, Dict, Any
import httpx
from collection_helper.core.models import LLMConfig
from collection_helper.logger import get_logger

logger = get_logger()


class LLMClient:
    """Client for interacting with various LLM providers."""

    def __init__(self, config: LLMConfig):
        """Initialize the LLM client.

        Args:
            config: LLM configuration
        """
        self.config = config
        self.client = httpx.AsyncClient(timeout=120.0)

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def generate_recommendations(
        self,
        items: List[Dict[str, Any]],
        count: int = 5,
        user_preferences: Optional[str] = None,
        category: str = "mixed",
        include_surprise: bool = False,
    ) -> str:
        """Generate recommendations based on available media.

        Args:
            items: List of media items (simplified format)
            count: Number of recommendations to generate based on collection patterns
            user_preferences: Optional user preferences/context
            category: Category type ("book", "video", or "mixed")
            include_surprise: Whether to add 1 surprise recommendation to diversify the collection

        Returns:
            LLM response as text
        """
        # Build the prompt
        prompt = self._build_prompt(items, count, user_preferences, category, include_surprise)

        try:
            # Anthropic has a different API format
            if self.config.provider == "anthropic":
                return await self._call_anthropic(prompt)
            # Ollama has a different API format
            elif self.config.provider == "ollama":
                return await self._call_ollama(prompt)
            # Everything else uses OpenAI-compatible format (openai, deepseek, groq, etc.)
            else:
                return await self._call_openai_compatible(prompt)
        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            raise

    def _build_prompt(
        self,
        items: List[Dict[str, Any]],
        count: int,
        user_preferences: Optional[str],
        category: str,
        include_surprise: bool = False,
    ) -> str:
        """Build the prompt for the LLM.

        Args:
            items: List of media items
            count: Number of recommendations
            user_preferences: Optional user preferences
            category: Category type ("book", "video", or "mixed")
            include_surprise: Whether to add 1 surprise recommendation

        Returns:
            Formatted prompt string
        """
        # Build the items list based on category
        if category == "book":
            category_name = "Books"
            items_sample = items[:30]  # Sample for analysis
            items_text = "\n".join(
                f"- {item['name']}" +
                (f" by {', '.join(item.get('authors', []))}" if item.get('authors') else "") +
                (f" - {item.get('genres', [])[:3]}" if item.get('genres') else "")
                for item in items_sample
            )
            recommendation_type = "books"
        elif category == "video":
            category_name = "Movies & TV Shows"
            items_sample = items[:30]  # Sample for analysis
            items_text = "\n".join(
                f"- {item['name']}" +
                (f" ({item.get('media_type', 'video')})" if item.get('media_type') else "") +
                (f" - {item.get('genres', [])[:3]}" if item.get('genres') else "")
                for item in items_sample
            )
            recommendation_type = "movies and TV shows"
        else:  # mixed
            # Separate items by source for better organization
            emby_items = [item for item in items if item.get('source') == 'emby']
            booklore_items = [item for item in items if item.get('source') == 'booklore']

            # Build categorized list
            items_sections = []

            if emby_items:
                emby_sample = emby_items[:30]  # Sample for analysis
                emby_text = "\n".join(
                    f"- {item['name']}" +
                    (f" ({item.get('media_type', 'video')})" if item.get('media_type') else "") +
                    (f" - {item.get('genres', [])[:3]}" if item.get('genres') else "")
                    for item in emby_sample
                )
                items_sections.append(f"Current Movies & TV Shows:\n{emby_text}")

            if booklore_items:
                books_sample = booklore_items[:30]  # Sample for analysis
                books_text = "\n".join(
                    f"- {item['name']}" +
                    (f" by {', '.join(item.get('authors', []))}" if item.get('authors') else "") +
                    (f" - {item.get('genres', [])[:3]}" if item.get('genres') else "")
                    for item in books_sample
                )
                items_sections.append(f"Current Books:\n{books_text}")

            items_text = "\n\n".join(items_sections)
            category_name = "Media Collection"
            recommendation_type = "items"

        prompt = f"""You are a media recommendation expert. Analyze the user's current {category_name} below and suggest NEW {recommendation_type} they might enjoy acquiring.

Their Current {category_name}:
{items_text}

Based on their collection's themes, genres, and authors, suggest {count} NEW {recommendation_type} they DON'T have but would likely enjoy.
"""

        if include_surprise:
            prompt += f"""Then, suggest 1 ADDITIONAL recommendation that is DIFFERENT from their usual patterns - something that would diversify their collection and expose them to a new genre, style, or perspective they haven't explored much.
"""

        prompt += f"""IMPORTANT:
- Suggest items NOT listed above (new discoveries for them)
- Consider patterns in their collection (genres, authors, themes)
- Be specific with titles - these should be real, well-known works
"""

        if user_preferences:
            prompt += f"Additional Context:\n{user_preferences}\n"

        if include_surprise:
            prompt += f"""Provide recommendations in this JSON format:
{{
  "recommendations": [
    {{
      "name": "Title of the {recommendation_type}",
      "reason": "Why they would like this based on their collection patterns (1-2 sentences)",
      "match_score": 0.85
    }}
  ]
}}

The LAST recommendation should be the SURPRISE recommendation that diversifies their collection.

Respond ONLY with valid JSON."""
        else:
            prompt += f"""Provide recommendations in this JSON format:
{{
  "recommendations": [
    {{
      "name": "Title of the {recommendation_type}",
      "reason": "Why they would like this based on their collection patterns (1-2 sentences)",
      "match_score": 0.85
    }}
  ]
}}

Respond ONLY with valid JSON."""

        return prompt

    async def _call_openai_compatible(self, prompt: str) -> str:
        """Call OpenAI-compatible API.

        Works with OpenAI, DeepSeek, Groq, and any other OpenAI-compatible provider.

        Args:
            prompt: The prompt to send

        Returns:
            LLM response text
        """
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        }

        data = {
            "model": self.config.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
        }

        # Use provided base_url or default to OpenAI
        base_url = self.config.base_url or "https://api.openai.com/v1"
        response = await self.client.post(
            f"{base_url}/chat/completions",
            headers=headers,
            json=data,
        )
        response.raise_for_status()
        result = response.json()

        return result["choices"][0]["message"]["content"]

    async def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API.

        Args:
            prompt: The prompt to send

        Returns:
            LLM response text
        """
        headers = {
            "x-api-key": self.config.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }

        data = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": self.config.temperature,
        }

        base_url = self.config.base_url or "https://api.anthropic.com/v1"
        response = await self.client.post(
            f"{base_url}/messages",
            headers=headers,
            json=data,
        )
        response.raise_for_status()
        result = response.json()

        return result["content"][0]["text"]

    async def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API.

        Args:
            prompt: The prompt to send

        Returns:
            LLM response text
        """
        base_url = self.config.base_url or "http://localhost:11434"

        data = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": self.config.max_tokens,
                "temperature": self.config.temperature,
            },
        }

        response = await self.client.post(
            f"{base_url}/api/generate",
            json=data,
        )
        response.raise_for_status()
        result = response.json()

        return result.get("response", "")
