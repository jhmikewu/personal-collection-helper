#!/usr/bin/env python3
"""Test script to check if the application starts properly."""

import sys

try:
    print("Testing imports...")
    from collection_helper.config import get_settings
    print("✓ Config imported")

    settings = get_settings()
    print(f"✓ Settings loaded: port={settings.port}, host={settings.host}")

    from collection_helper.logger import setup_logging, get_logger
    print("✓ Logger module imported")

    setup_logging()
    print("✓ Logging setup complete")

    logger = get_logger()
    logger.info("Test log message")
    print("✓ Logger working")

    from collection_helper.web import app
    print("✓ FastAPI app created")

    from collection_helper.web import run_server
    print("✓ run_server function available")

    print("\n✓ All imports successful!")
    print(f"\nTo start the server manually, run:")
    print(f"  python -c 'from collection_helper.web import run_server; run_server()'")

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
