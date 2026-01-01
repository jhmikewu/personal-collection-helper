#!/bin/bash

# Start script for the Collection Helper

# Check if we should run web server or CLI
if [ "$1" = "cli" ]; then
    # Run CLI with passed arguments
    shift
    python -m collection_helper "$@"
else
    # Run web server by default
    python -m collection_helper.web
fi
