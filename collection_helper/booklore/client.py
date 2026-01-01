"""Booklore client."""

from typing import List, Optional, Dict, Any
import httpx
from collection_helper.config import get_settings
from collection_helper.booklore.models import BookloreBook, BookloreSeries, BookloreCollection
from collection_helper.logger import get_logger

logger = get_logger()


class BookloreClient:
    """Client for interacting with Booklore.

    Note: Booklore may not have a public API. This implementation assumes
    a hypothetical API structure. Adjust based on actual Booklore API.
    """

    def __init__(self):
        """Initialize the Booklore client."""
        settings = get_settings()
        self.base_url = settings.booklore_url.rstrip("/")
        self.api_key = settings.booklore_api_key
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Accept": "application/json",
            },
            timeout=30.0,
        )

        # Add API key header if available
        if self.api_key:
            self.client.headers["Authorization"] = f"Bearer {self.api_key}"

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def _request(
        self, method: str, endpoint: str, **kwargs
    ) -> Dict[str, Any]:
        """Make a request to Booklore.

        Args:
            method: HTTP method
            endpoint: API endpoint path
            **kwargs: Additional arguments for httpx

        Returns:
            JSON response as dictionary

        Raises:
            httpx.HTTPError: If the request fails
        """
        url = endpoint
        logger.debug(f"Making {method} request to {url}")

        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Booklore request failed: {e}")
            raise

    async def get_books(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> List[BookloreBook]:
        """Get all books from Booklore.

        Args:
            limit: Maximum number of books to return
            offset: Number of books to skip

        Returns:
            List of books
        """
        try:
            params = {
                "page": offset // limit + 1 if limit > 0 else 1,
                "size": limit,
            }
            data = await self._request("GET", "/api/v1/books", params=params)

            # Handle both paginated response (dict with 'content') and direct list
            if isinstance(data, list):
                books = data
            else:
                books = data.get("content", [])

            # Log first book to debug field names
            if books:
                logger.debug(f"First book data: {books[0]}")

            book_objects = [BookloreBook(**book) for book in books]
            logger.info(f"Retrieved {len(book_objects)} books from Booklore")
            return book_objects
        except Exception as e:
            logger.error(f"Failed to retrieve books: {e}")
            return []

    async def get_book(self, book_id: str) -> Optional[BookloreBook]:
        """Get a specific book by ID.

        Args:
            book_id: Book ID

        Returns:
            Book or None if not found
        """
        try:
            data = await self._request("GET", f"/api/v1/books/{book_id}")
            return BookloreBook(**data)
        except httpx.HTTPError as e:
            logger.error(f"Failed to retrieve book {book_id}: {e}")
            return None

    async def search_books(
        self,
        query: str,
        limit: int = 20,
    ) -> List[BookloreBook]:
        """Search for books in Booklore.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching books
        """
        try:
            params = {
                "query": query,
                "page": 0,
                "size": limit,
            }
            data = await self._request("GET", "/api/v1/books/search", params=params)

            # Handle both paginated response and direct list
            if isinstance(data, list):
                books = data
            else:
                books = data.get("content", [])

            book_objects = [BookloreBook(**book) for book in books]
            logger.info(f"Found {len(book_objects)} books matching '{query}'")
            return book_objects
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    async def get_collections(self) -> List[BookloreCollection]:
        """Get all collections from Booklore.

        Returns:
            List of collections
        """
        try:
            # Booklore doesn't have a separate collections endpoint
            # Return empty list for now
            logger.info("Booklore doesn't have separate collections - using series instead")
            return []
        except Exception as e:
            logger.error(f"Failed to retrieve collections: {e}")
            return []

    async def get_series(self) -> List[BookloreSeries]:
        """Get all series from Booklore.

        Returns:
            List of series
        """
        try:
            # Try the series endpoint
            data = await self._request("GET", "/api/v1/series")

            # Handle both paginated response and direct list
            if isinstance(data, list):
                series_list = data
            else:
                series_list = data.get("content", [])

            series_objects = [BookloreSeries(**series) for series in series_list]
            logger.info(f"Retrieved {len(series_objects)} series from Booklore")
            return series_objects
        except Exception as e:
            logger.error(f"Failed to retrieve series: {e}")
            return []

    async def health_check(self) -> bool:
        """Check if Booklore is accessible.

        Returns:
            True if accessible, False otherwise
        """
        try:
            await self._request("GET", "/api/v1/healthcheck")
            logger.info("Booklore health check passed")
            return True
        except Exception as e:
            logger.error(f"Booklore health check failed: {e}")
            return False
