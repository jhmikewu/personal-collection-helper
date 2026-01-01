"""Tests for Emby client."""

import pytest
from collection_helper.emby.client import EmbyClient
from collection_helper.emby.models import EmbyMediaItem, EmbyLibrary


@pytest.mark.asyncio
async def test_emby_client_initialization():
    """Test that Emby client initializes correctly."""
    client = EmbyClient()
    assert client.api_key is not None
    assert client.base_url is not None
    await client.close()


def test_emby_media_item_model():
    """Test EmbyMediaItem model."""
    item = EmbyMediaItem(
        id="123",
        name="Test Movie",
        type="Movie",
        media_type="Video",
        production_year=2020,
        community_rating=8.5,
    )

    assert item.id == "123"
    assert item.name == "Test Movie"
    assert item.production_year == 2020
    assert item.community_rating == 8.5


def test_emby_library_model():
    """Test EmbyLibrary model."""
    library = EmbyLibrary(
        id="456",
        name="Movies",
        type="CollectionFolder",
        collection_type="movies",
        locations=["/path/to/movies"],
    )

    assert library.id == "456"
    assert library.name == "Movies"
    assert library.collection_type == "movies"
