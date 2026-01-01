# Personal Collection Helper

A Python-based tool for managing media libraries across Emby and Booklore, packaged as a Docker container for easy deployment on NAS devices.

## Features

- **Unified Search**: Search across both Emby and Booklore simultaneously
- **Library Management**: Browse and organize your media collections
- **REST API**: FastAPI-based web API for integration with other tools
- **CLI Interface**: Command-line interface for direct interaction
- **Statistics**: Get insights about your media collections
- **Health Monitoring**: Check service availability and status
- **NAS-Ready**: Packaged as a Docker container for easy deployment

## Architecture

```
personal-collection-helper/
├── collection_helper/
│   ├── emby/           # Emby API client
│   ├── booklore/       # Booklore client
│   ├── core/           # Media management logic
│   ├── cli.py          # Command-line interface
│   ├── web.py          # FastAPI web server
│   ├── config.py       # Configuration management
│   └── logger.py       # Logging setup
├── tests/              # Test suite
├── Dockerfile          # Container image
└── docker-compose.yml  # Deployment config
```

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/personal-collection-helper.git
cd personal-collection-helper
```

### 2. Configure Environment Variables

Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```bash
EMBY_URL=http://your-emby-server:8096
EMBY_API_KEY=your_emby_api_key_here
BOOKLORE_URL=http://your-booklore-server:8080
BOOKLORE_API_KEY=
LOG_LEVEL=INFO
```

### 3. Run with Docker Compose (Recommended)

```bash
docker-compose up -d
```

The API will be available at `http://localhost:8080`

### 4. Run with Docker CLI

```bash
docker build -t collection-helper .
docker run -d \
  --name collection-helper \
  -p 8080:8080 \
  -v $(pwd)/config:/app/config \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  collection-helper
```

## Usage

### Web API

Once running, access the interactive API documentation at:
- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

#### Example API Requests

```bash
# Health check
curl http://localhost:8080/health

# Search across all collections
curl -X POST http://localhost:8080/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Matrix", "emby": true, "booklore": true}'

# Get Emby libraries
curl http://localhost:8080/emby/libraries

# Get Emby items from specific library
curl http://localhost:8080/emby/items?library=Movies&limit=50

# Get Booklore books
curl http://localhost:8080/booklore/books?limit=100

# Get collection statistics
curl http://localhost:8080/stats
```

### Command-Line Interface

```bash
# Show all available commands
docker exec collection-helper python -m collection_helper --help

# Search across all platforms
docker exec collection-helper python -m collection_helper search "Matrix"

# List Emby media items
docker exec collection-helper python -m collection_helper list-emby

# List items from specific library
docker exec collection_helper python -m collection_helper list-emby --library Movies

# List Booklore books
docker exec collection-helper python -m collection_helper list-books

# Show all libraries
docker exec collection-helper python -m collection_helper libraries

# Display collection statistics
docker exec collection-helper python -m collection_helper stats

# Check service health
docker exec collection-helper python -m collection_helper health
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Or install with development dependencies
pip install -e ".[dev]"

# Run the web server
python -m collection_helper.web

# Run the CLI
python -m collection_helper search "test query"

# Run tests
pytest

# Run tests with coverage
pytest --cov=collection_helper

# Format code
black collection_helper tests

# Lint code
flake8 collection_helper tests
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `EMBY_URL` | Yes | - | URL to your Emby server |
| `EMBY_API_KEY` | Yes | - | Your Emby API key |
| `BOOKLORE_URL` | Yes | - | URL to your Booklore instance |
| `BOOKLORE_API_KEY` | No | - | Booklore API key (if required) |
| `HOST` | No | 0.0.0.0 | Host to bind the web server to |
| `PORT` | No | 8080 | Port for the web server |
| `LOG_LEVEL` | No | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |

### Getting Your Emby API Key

1. Log in to your Emby server
2. Go to Settings → Advanced → API Keys
3. Click "Add API Key"
4. Give it a name and copy the key

## API Endpoints

### Health & Info
- `GET /` - API information
- `GET /health` - Service health status

### Search & Browse
- `POST /search` - Search across all collections
- `GET /emby/libraries` - List Emby libraries
- `GET /emby/items` - Get Emby media items
- `GET /booklore/books` - Get Booklore books
- `GET /stats` - Collection statistics

## Development

### Project Structure

```
collection_helper/
├── __init__.py
├── __main__.py
├── cli.py              # Click-based CLI
├── web.py              # FastAPI application
├── config.py           # Pydantic settings
├── logger.py           # Loguru configuration
├── core/
│   ├── __init__.py
│   └── manager.py      # MediaManager orchestration
├── emby/
│   ├── __init__.py
│   ├── client.py       # Emby API client
│   └── models.py       # Emby data models
└── booklore/
    ├── __init__.py
    ├── client.py       # Booklore client
    └── models.py       # Booklore data models
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_config.py

# Run with coverage
pytest --cov=collection_helper --cov-report=html

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code with Black
make black

# Lint with flake8
make flake8

# Type check with mypy
make mypy
```

## Docker Deployment

### Building the Image

```bash
docker build -t collection-helper:latest .
```

### Running the Container

```bash
# Using docker-compose
docker-compose up -d

# Using docker run
docker run -d \
  --name collection-helper \
  --restart unless-stopped \
  -p 8080:8080 \
  -v /path/to/config:/app/config \
  -v /path/to/logs:/app/logs \
  --env-file .env \
  collection-helper:latest
```

### Viewing Logs

```bash
# Follow logs
docker-compose logs -f

# View last 100 lines
docker-compose logs --tail=100
```

### Stopping the Container

```bash
docker-compose down
```

## Troubleshooting

### Connection Issues

If you're having trouble connecting to Emby or Booklore:

1. Check that the URLs are correct and accessible from within the container
2. Verify API keys are correct
3. Check the logs: `docker-compose logs -f`
4. Test connectivity: `docker exec collection-helper python -m collection_helper health`

### Common Issues

**Issue**: "Connection refused" to Emby/Booklore
- **Solution**: Use service names instead of localhost if running in Docker Compose

**Issue**: "401 Unauthorized" from Emby
- **Solution**: Verify your Emby API key is valid and has appropriate permissions

**Issue**: Booklore returns no results
- **Solution**: The Booklore API structure may vary. Check the logs for specific errors

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details

## Acknowledgments

- [Emby](https://emby.media/) - Media server
- [Booklore](https://github.com/bookloreapp/booklore) - Book management
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Click](https://click.palletsprojects.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal formatting
