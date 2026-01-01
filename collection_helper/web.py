"""Web API interface."""

from contextlib import asynccontextmanager
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from collection_helper.config import get_settings
from collection_helper.logger import setup_logging, get_logger
from collection_helper.core.manager import MediaManager

# Setup logging
setup_logging()
logger = get_logger()


class SearchRequest(BaseModel):
    """Search request model."""

    query: str = Field(..., description="Search query")
    emby: bool = Field(True, description="Search in Emby")
    booklore: bool = Field(True, description="Search in Booklore")


class HealthResponse(BaseModel):
    """Health check response model."""

    emby: bool
    booklore: bool


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    logger.info("Starting Collection Helper API")
    yield
    logger.info("Shutting down Collection Helper API")


# Create FastAPI app
app = FastAPI(
    title="Personal Collection Helper",
    description="API for managing media libraries across Emby and Booklore",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Personal Collection Helper API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check() -> HealthResponse:
    """Check health of connected services."""
    try:
        async with MediaManager() as manager:
            health = await manager.health_check()
            return HealthResponse(**health)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.post("/search")
async def search(request: SearchRequest) -> Dict[str, Any]:
    """Search across all collections.

    Args:
        request: Search request with query and platform filters

    Returns:
        Search results from all platforms
    """
    try:
        async with MediaManager() as manager:
            results = await manager.search_all(
                request.query,
                request.emby,
                request.booklore,
            )

            # Convert to JSON-serializable format
            serialized_results = {}
            for platform, items in results.items():
                serialized_results[platform] = [
                    item.model_dump(mode="json") for item in items
                ]

            return {
                "query": request.query,
                "results": serialized_results,
            }
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/emby/libraries")
async def get_emby_libraries():
    """Get all Emby libraries."""
    try:
        async with MediaManager() as manager:
            libraries = await manager.get_emby_libraries()
            return {"libraries": libraries}
    except Exception as e:
        logger.error(f"Failed to get libraries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/emby/items")
async def get_emby_items(
    library: str = None,
    limit: int = 100,
):
    """Get items from Emby.

    Args:
        library: Optional library name filter
        limit: Maximum number of items

    Returns:
        List of media items
    """
    try:
        async with MediaManager() as manager:
            items = await manager.get_emby_items(
                library_name=library,
                limit=limit,
            )

            return {
                "items": [item.model_dump(mode="json") for item in items],
                "count": len(items),
            }
    except Exception as e:
        logger.error(f"Failed to get items: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/booklore/books")
async def get_booklore_books(
    limit: int = 100,
):
    """Get books from Booklore.

    Args:
        limit: Maximum number of books

    Returns:
        List of books
    """
    try:
        async with MediaManager() as manager:
            books = await manager.get_booklore_books(limit=limit)

            return {
                "books": [book.model_dump(mode="json") for book in books],
                "count": len(books),
            }
    except Exception as e:
        logger.error(f"Failed to get books: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get collection statistics."""
    try:
        async with MediaManager() as manager:
            stats = await manager.get_collection_stats()
            return stats
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "collection_helper.web:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )


def run_server():
    """Run the FastAPI server - called from startup script."""
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower(),
    )
