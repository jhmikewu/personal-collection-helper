#!/bin/bash
# Update script for NAS

echo "🔄 Updating Personal Collection Helper..."

# Navigate to project directory
cd /mnt/user/docker/personal-collection-helper/personal-collection-helper || exit 1

# Pull latest changes
echo "📥 Pulling latest changes from GitHub..."
git pull origin main

# Rebuild and restart
echo "🔨 Rebuilding Docker container..."
docker compose down
docker compose up -d --build

echo "✅ Update complete!"
echo ""
echo "Container status:"
docker ps | grep collection-helper

echo ""
echo "Recent logs:"
docker logs collection-helper --tail 20
