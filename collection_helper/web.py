"""Web API interface."""

from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from collection_helper.config import get_settings
from collection_helper.logger import setup_logging, get_logger
from collection_helper.core.manager import MediaManager
from collection_helper.core.recommendations import RecommendationEngine
from collection_helper.core.models import LLMConfig

# Setup logging
try:
    setup_logging()
except Exception as e:
    print(f"Warning: Could not setup logging: {e}")
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


class RecommendationRequest(BaseModel):
    """Recommendation request model."""

    count: int = Field(5, description="Number of recommendations to generate PER CATEGORY based on collection patterns (plus 1 surprise recommendation per category)", ge=1, le=20)
    user_preferences: Optional[str] = Field(None, description="Optional user preferences/context")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    logger.info("Starting Collection Helper API")
    yield
    logger.info("Shutting down Collection Helper API")


# Define tags for API organization
tags_metadata = [
    {
        "name": "General",
        "description": "General endpoints for health, search, and statistics",
    },
    {
        "name": "Emby",
        "description": "Endpoints for interacting with Emby media server",
    },
    {
        "name": "Booklore",
        "description": "Endpoints for interacting with Booklore book management",
    },
]

# Create FastAPI app
app = FastAPI(
    title="Personal Collection Helper",
    description="API for managing media libraries across Emby and Booklore",
    version="0.1.0",
    lifespan=lifespan,
    openapi_tags=tags_metadata,
)


@app.get("/", tags=["General"])
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Personal Collection Helper API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["General"])
async def health_check() -> HealthResponse:
    """Check health of connected services."""
    try:
        async with MediaManager() as manager:
            health = await manager.health_check()
            return HealthResponse(**health)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.post("/search", tags=["General"])
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


@app.get("/emby/libraries", tags=["Emby"])
async def get_emby_libraries():
    """Get all Emby libraries."""
    try:
        async with MediaManager() as manager:
            libraries = await manager.get_emby_libraries()
            return {
                "libraries": [lib.model_dump(mode="json") for lib in libraries],
                "count": len(libraries),
            }
    except Exception as e:
        logger.error(f"Failed to get libraries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/emby/items", tags=["Emby"])
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


@app.get("/booklore/libraries", tags=["Booklore"])
async def get_booklore_libraries():
    """Get libraries from Booklore.

    Returns:
        List of libraries with stats
    """
    try:
        async with MediaManager() as manager:
            libraries = await manager.booklore.get_libraries()

            return {
                "libraries": [lib.model_dump(mode="json") for lib in libraries],
                "count": len(libraries),
            }
    except Exception as e:
        logger.error(f"Failed to get Booklore libraries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/booklore/books", tags=["Booklore"])
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


@app.get("/stats", tags=["General"])
async def get_stats():
    """Get collection statistics."""
    try:
        async with MediaManager() as manager:
            stats = await manager.get_collection_stats()
            return stats
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommendations", tags=["General"])
async def generate_recommendations(request: RecommendationRequest):
    """Generate daily recommendations using LLM.

    Args:
        request: Recommendation request with count and optional preferences

    Returns:
        Daily recommendations from the collection
    """
    try:
        settings = get_settings()

        # Check if LLM is configured
        if not settings.llm_api_key:
            raise HTTPException(
                status_code=400,
                detail="LLM API key not configured. Please set LLM_API_KEY in your environment.",
            )

        # Create LLM config
        llm_config = LLMConfig(
            provider=settings.llm_provider,
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            model=settings.llm_model,
            max_tokens=settings.llm_max_tokens,
            temperature=settings.llm_temperature,
        )

        # Generate recommendations
        engine = RecommendationEngine(llm_config)
        recommendations = await engine.generate_daily_recommendations(
            count=request.count,
            user_preferences=request.user_preferences,
        )

        return recommendations.model_dump(mode="json")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate recommendations: {e}")
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
    import sys

    settings = get_settings()

    logger.info(f"Starting Personal Collection Helper API on {settings.host}:{settings.port}")
    logger.info(f"API documentation available at: http://{settings.host}:{settings.port}/docs")

    try:
        uvicorn.run(
            app,
            host=settings.host,
            port=settings.port,
            log_level=settings.log_level.lower(),
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)
