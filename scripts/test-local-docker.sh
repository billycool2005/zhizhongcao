#!/bin/bash
# Zhizhongcao - Local Docker Test Script
# Emergency Mode: Run continuously until Alpha ready!

set -e

echo "🚀 Starting Zhizhongcao Docker test..."
echo "Date: $(date)"
echo "Mode: NO SLEEP MODE 🔥"

cd "$(dirname "$0")/../backend"

# Build and run
echo "Building Docker image..."
docker-compose build --no-cache

echo "Starting services..."
docker-compose up -d

# Wait for health check
echo "Waiting for API to be ready..."
for i in {1..60}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ FastAPI health check passed!"
        break
    fi
    echo "⏳ Waiting... ($i/60)"
    sleep 5
done

# Test API endpoints
echo ""
echo "Testing API endpoints..."
curl -s http://localhost:8000/ | jq . || true
curl -s http://localhost:8000/health | jq . || true

echo ""
echo "🎉 Local Docker test COMPLETE!"
echo "Access API docs at: http://localhost:8000/docs"
echo "Next step: Seed user recruitment & AI integration"

# Keep container running (don't stop)
tail -f /dev/null
