"""Media management coordinator."""

from typing import List, Dict, Any, Optional
from collection_helper.emby import EmbyClient
from collection_helper.booklore import BookloreClient
from collection_helper.emby.models import EmbyMediaItem
from collection_helper.booklore.models import BookloreBook
from collection_helper.logger import get_logger

logger = get_logger()


class MediaManager:
    """Manages media across Emby and Booklore."""

    def __init__(self):
        """Initialize the media manager."""
        self.emby: Optional[EmbyClient] = None
        self.booklore: Optional[BookloreClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.emby = EmbyClient()
        self.booklore = BookloreClient()
        await self.emby.__aenter__()
        await self.booklore.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.emby:
            await self.emby.__aexit__(exc_type, exc_val, exc_tb)
        if self.booklore:
            await self.booklore.__aexit__(exc_type, exc_val, exc_tb)

    async def search_all(
        self,
        query: str,
        search_emby: bool = True,
        search_booklore: bool = True,
    ) -> Dict[str, List[Any]]:
        """Search across all configured platforms.

        Args:
            query: Search query
            search_emby: Whether to search Emby
            search_booklore: Whether to search Booklore

        Returns:
            Dictionary with platform names as keys and results as values
        """
        results = {}

        if search_emby and self.emby:
            try:
                emby_results = await self.emby.search_items(query)
                results["emby"] = emby_results
                logger.info(f"Found {len(emby_results)} results in Emby")
            except Exception as e:
                logger.error(f"Emby search failed: {e}")
                results["emby"] = []

        if search_booklore and self.booklore:
            try:
                booklore_results = await self.booklore.search_books(query)
                results["booklore"] = booklore_results
                logger.info(f"Found {len(booklore_results)} results in Booklore")
            except Exception as e:
                logger.error(f"Booklore search failed: {e}")
                results["booklore"] = []

        return results

    async def get_emby_libraries(self) -> List[str]:
        """Get list of Emby library names.

        Returns:
            List of library names
        """
        if not self.emby:
            return []

        try:
            libraries = await self.emby.get_libraries()
            return [lib.name for lib in libraries]
        except Exception as e:
            logger.error(f"Failed to get Emby libraries: {e}")
            return []

    async def get_emby_items(
        self,
        library_name: Optional[str] = None,
        limit: int = 100,
    ) -> List[EmbyMediaItem]:
        """Get items from Emby, optionally filtered by library.

        Args:
            library_name: Library name to filter by
            limit: Maximum number of items

        Returns:
            List of media items
        """
        if not self.emby:
            return []

        try:
            if library_name:
                # Find library by name
                libraries = await self.emby.get_libraries()
                library = next((lib for lib in libraries if lib.name == library_name), None)
                if not library:
                    logger.warning(f"Library '{library_name}' not found")
                    return []
                return await self.emby.get_library_items(library.id, limit=limit)
            else:
                # Get items from all libraries
                libraries = await self.emby.get_libraries()
                all_items = []
                for library in libraries:
                    items = await self.emby.get_library_items(library.id, limit=limit)
                    all_items.extend(items)
                return all_items
        except Exception as e:
            logger.error(f"Failed to get Emby items: {e}")
            return []

    async def get_booklore_books(
        self,
        limit: int = 100,
    ) -> List[BookloreBook]:
        """Get books from Booklore.

        Args:
            limit: Maximum number of books

        Returns:
            List of books
        """
        if not self.booklore:
            return []

        try:
            return await self.booklore.get_books(limit=limit)
        except Exception as e:
            logger.error(f"Failed to get Booklore books: {e}")
            return []

    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about all collections.

        Returns:
            Dictionary with collection statistics
        """
        stats = {
            "emby": {
                "libraries": [],
                "total_items": 0,
            },
            "booklore": {
                "total_books": 0,
                "collections": [],
            },
        }

        if self.emby:
            try:
                libraries = await self.emby.get_libraries()
                stats["emby"]["libraries"] = [lib.name for lib in libraries]
                total_items = 0
                for lib in libraries:
                    items = await self.emby.get_library_items(lib.id, limit=1000)
                    total_items += len(items)
                stats["emby"]["total_items"] = total_items
            except Exception as e:
                logger.error(f"Failed to get Emby stats: {e}")

        if self.booklore:
            try:
                books = await self.booklore.get_books(limit=1000)
                stats["booklore"]["total_books"] = len(books)
                collections = await self.booklore.get_collections()
                stats["booklore"]["collections"] = [col.name for col in collections]
            except Exception as e:
                logger.error(f"Failed to get Booklore stats: {e}")

        return stats

    async def health_check(self) -> Dict[str, bool]:
        """Check health of all connected services.

        Returns:
            Dictionary with service names as keys and health status as values
        """
        health = {}

        if self.emby:
            health["emby"] = await self.emby.health_check()

        if self.booklore:
            health["booklore"] = await self.booklore.health_check()

        return health
