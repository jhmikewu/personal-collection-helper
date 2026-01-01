# Quick Start Guide

This guide will help you get up and running with Personal Collection Helper in just a few minutes.

## Prerequisites

- Docker and Docker Compose installed on your NAS or system
- Access to an Emby server
- Access to a Booklore instance
- (Optional) LLM API key for AI-powered recommendations

## Setup in 3 Steps

### Step 1: Create Configuration File

```bash
cp .env.example .env
```

**Security Note**: The `.env` file is in `.gitignore` and will NOT be uploaded to GitHub. Your API keys are safe!

### Step 2: Edit Configuration

Open `.env` in a text editor and add your details:

```bash
# Required: Emby Configuration
EMBY_URL=http://your-emby-server:8096
EMBY_API_KEY=your_emby_api_key_here

# Required: Booklore Configuration
BOOKLORE_URL=http://your-booklore-server:6060
BOOKLORE_API_KEY=your_booklore_api_token

# Optional: Server Settings
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8090

# Optional: LLM Configuration for AI Recommendations
LLM_PROVIDER=openai
LLM_API_KEY=your_llm_api_key
LLM_BASE_URL=
LLM_MODEL=gpt-4o-mini
```

**Getting your Emby API Key:**
1. Open Emby in your browser
2. Go to Settings → Advanced → API Keys
3. Click "Add API Key"
4. Name it "Collection Helper" and click Save
5. Copy the generated key to your `.env` file

**Getting your Booklore API Token:**
1. Open Booklore in your browser
2. Go to Settings → API
3. Generate a new token
4. Copy the token to your `.env` file

### Step 3: Start the Container

```bash
docker-compose up -d
```

That's it! The service will now be available at http://localhost:8090

**Note**: Default port is 8090 (changed from 8080 to avoid conflicts with qBittorrent).

## Next Steps

### Test the Service

Open http://localhost:8090/docs in your browser to see the interactive API documentation.

### Try Your First Search

Using the API documentation (Swagger UI):
1. Click on `POST /search`
2. Click "Try it out"
3. Enter a search term like "Matrix"
4. Click "Execute"
5. View results from both Emby and Booklore!

### Try AI Recommendations (Optional)

If you configured LLM settings:
1. Click on `POST /recommendations`
2. Click "Try it out"
3. Enter `{"count": 5}` in the request body
4. Click "Execute"
5. Get 6 book recommendations + 6 video recommendations (12 total)!
   - 5 pattern-based recommendations per category
   - 1 surprise recommendation per category to diversify your collection

See [RECOMMENDATIONS.md](RECOMMENDATIONS.md) for details on the recommendation feature.

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

### Recommendations not working
- Verify LLM_API_KEY is set in `.env`
- Check that LLM_PROVIDER and LLM_MODEL are correct
- Ensure LLM_BASE_URL points to the correct API endpoint
- Review logs: `docker-compose logs -f | grep recommendations`

### Need more help?
- Main documentation: [README.md](README.md)
- Recommendations guide: [RECOMMENDATIONS.md](RECOMMENDATIONS.md)
