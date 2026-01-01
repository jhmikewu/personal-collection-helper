"""Emby API client."""

from typing import List, Optional, Dict, Any
import httpx
from collection_helper.config import get_settings
from collection_helper.emby.models import EmbyMediaItem, EmbyLibrary, EmbyUser
from collection_helper.logger import get_logger

logger = get_logger()


class EmbyClient:
    """Client for interacting with the Emby API."""

    def __init__(self):
        """Initialize the Emby client."""
        settings = get_settings()
        self.base_url = settings.emby_url.rstrip("/")
        self.api_key = settings.emby_api_key
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "X-Emby-Token": self.api_key,
                "Accept": "application/json",
            },
            timeout=30.0,
        )

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
        """Make a request to the Emby API.

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
            logger.error(f"Emby API request failed: {e}")
            raise

    async def get_libraries(self) -> List[EmbyLibrary]:
        """Get all libraries from Emby.

        Returns:
            List of Emby libraries
        """
        try:
            # Use the Library/MediaFolders endpoint to get all libraries
            data = await self._request("GET", "/Library/MediaFolders")
            items = data.get("Items", [])

            logger.debug(f"Total items returned: {len(items)}")

            libraries = [EmbyLibrary(**item) for item in items]
            logger.info(f"Retrieved {len(libraries)} libraries from Emby")
            return libraries
        except Exception as e:
            logger.error(f"Failed to retrieve libraries: {e}")
            return []

    async def get_library_items(
        self,
        library_id: str,
        limit: int = 100,
        offset: int = 0,
    ) -> List[EmbyMediaItem]:
        """Get items from a specific library.

        Args:
            library_id: Library ID
            limit: Maximum number of items to return
            offset: Number of items to skip

        Returns:
            List of media items
        """
        try:
            params = {
                "ParentId": library_id,
                "Limit": limit,
                "StartIndex": offset,
                "IncludeItemTypes": "Movie,Series,Book",
            }
            data = await self._request("GET", "/Items", params=params)
            items = data.get("Items", [])
            media_items = [EmbyMediaItem(**item) for item in items]
            logger.info(f"Retrieved {len(media_items)} items from library {library_id}")
            return media_items
        except Exception as e:
            logger.error(f"Failed to retrieve library items: {e}")
            return []

    async def get_item(self, item_id: str) -> Optional[EmbyMediaItem]:
        """Get a specific item by ID.

        Args:
            item_id: Item ID

        Returns:
            Media item or None if not found
        """
        try:
            data = await self._request("GET", f"/Items/{item_id}")
            return EmbyMediaItem(**data)
        except httpx.HTTPError as e:
            logger.error(f"Failed to retrieve item {item_id}: {e}")
            return None

    async def search_items(
        self,
        query: str,
        item_types: Optional[List[str]] = None,
        limit: int = 20,
    ) -> List[EmbyMediaItem]:
        """Search for items in Emby.

        Args:
            query: Search query
            item_types: List of item types to search (Movie, Series, Book, etc.)
            limit: Maximum number of results

        Returns:
            List of matching media items
        """
        try:
            params = {
                "SearchTerm": query,
                "Limit": limit,
                "Recursive": True,
            }
            if item_types:
                params["IncludeItemTypes"] = ",".join(item_types)

            data = await self._request("GET", "/Items", params=params)
            items = data.get("Items", [])
            media_items = [EmbyMediaItem(**item) for item in items]
            logger.info(f"Found {len(media_items)} items matching '{query}'")
            return media_items
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    async def get_users(self) -> List[EmbyUser]:
        """Get all users from Emby.

        Returns:
            List of Emby users
        """
        try:
            data = await self._request("GET", "/Users")
            users = [EmbyUser(**user) for user in data]
            logger.info(f"Retrieved {len(users)} users from Emby")
            return users
        except Exception as e:
            logger.error(f"Failed to retrieve users: {e}")
            return []

    async def health_check(self) -> bool:
        """Check if Emby server is accessible.

        Returns:
            True if server is accessible, False otherwise
        """
        try:
            await self._request("GET", "/System/Info")
            logger.info("Emby server health check passed")
            return True
        except Exception as e:
            logger.error(f"Emby server health check failed: {e}")
            return False
