# Quick Start Guide

This guide will help you get up and running with Personal Collection Helper in just a few minutes.

## Prerequisites

- Docker and Docker Compose installed on your NAS or system
- Access to an Emby server
- (Optional) Access to a Booklore instance

## Setup in 3 Steps

### Step 1: Create Configuration File

```bash
cp .env.example .env
```

### Step 2: Edit Configuration

Open `.env` in a text editor and add your details:

```bash
# Required: Emby Configuration
EMBY_URL=http://localhost:8096
EMBY_API_KEY=your_emby_api_key_here

# Required: Booklore Configuration
BOOKLORE_URL=http://localhost:8080
BOOKLORE_API_KEY=

# Optional: Advanced Settings
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8080
```

**Getting your Emby API Key:**
1. Open Emby in your browser
2. Go to Settings → Advanced → API Keys
3. Click "Add API Key"
4. Name it "Collection Helper" and click Save
5. Copy the generated key to your `.env` file

### Step 3: Start the Container

```bash
docker-compose up -d
```

That's it! The service will now be available at http://localhost:8080

## Next Steps

### Test the Service

Open http://localhost:8080/docs in your browser to see the interactive API documentation.

### Try Your First Search

Using the API documentation (Swagger UI):
1. Click on `POST /search`
2. Click "Try it out"
3. Enter a search term like "Matrix"
4. Click "Execute"
5. View results from both Emby and Booklore!

### Using the Command Line

```bash
# Search for content
docker exec collection-helper python -m collection_helper search "Matrix"

# List all libraries
docker exec collection-helper python -m collection_helper libraries

# View statistics
docker exec collection-helper python -m collection_helper stats

# Check health
docker exec collection-helper python -m collection_helper health
```

## Troubleshooting

### Container won't start
```bash
# Check logs
docker-compose logs -f

# Restart
docker-compose restart
```

### Can't connect to Emby
- Make sure `EMBY_URL` includes the port (typically :8096)
- If running in Docker, use the internal network address, not localhost
- Verify your API key is correct

### Need more help?
Check the main [README.md](README.md) for detailed documentation.
