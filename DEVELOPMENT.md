# Development Guide

## Local Development Workflow

### 1. Initial Setup

```bash
# Install dependencies locally
pip install -r requirements.txt

# Or create a virtual environment (recommended)
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your actual credentials:
```
EMBY_URL=http://192.168.50.16:8096
EMBY_API_KEY=your_actual_api_key
BOOKLORE_URL=http://192.168.50.16:6060
BOOKLORE_API_KEY=your_actual_token
```

### 3. Run Local Development Server

**Option A: Run directly with Python (simplest for development)**

```bash
# Set environment variables first
export EMBY_URL=http://192.168.50.16:8096
export EMBY_API_KEY=your_key
export BOOKLORE_URL=http://192.168.50.16:6060
export LOG_LEVEL=DEBUG

# Run the server
python -m collection_helper.web
```

Or on Windows PowerShell:
```powershell
$env:EMBY_URL="http://192.168.50.16:8096"
$env:EMBY_API_KEY="your_key"
$env:BOOKLORE_URL="http://192.168.50.16:6060"
$env:LOG_LEVEL="DEBUG"
python -m collection_helper.web
```

**Option B: Use Docker for local testing**

```bash
docker compose -f docker-compose.dev.yml up --build
```

### 4. Test the API

Once running, test at http://localhost:8090/docs

Or use curl:
```bash
# Health check
curl http://localhost:8090/health

# Get libraries
curl http://localhost:8090/emby/libraries

# Search
curl -X POST http://localhost:8090/search \
  -H "Content-Type: application/json" \
  -d '{"query":"matrix","emby":true,"booklore":true}'
```

### 5. Development Workflow

```bash
# 1. Make code changes
# 2. If running directly with Python, just restart the server
# 3. If using Docker, rebuild:
docker compose -f docker-compose.dev.yml up --build

# 4. Test locally until working
# 5. Commit changes
git add .
git commit -m "Description of changes"

# 6. Deploy to NAS
git push origin master
# Then on NAS:
ssh your_nas
cd /path/to/project
git pull
docker compose down
docker compose up -d --build
```

## Troubleshooting

### Port already in use
If port 8090 is in use locally, change it in `.env`:
```
PORT=8091
```

### Can't connect to Emby/Booklore
Make sure you're using the NAS IP address from your local machine:
```
EMBY_URL=http://192.168.50.16:8096
BOOKLORE_URL=http://192.168.50.16:6060
```

### Dependencies not found
```bash
pip install -r requirements.txt
```
