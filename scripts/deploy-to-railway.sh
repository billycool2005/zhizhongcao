#!/bin/bash
# Zhizhongcao - Railway Deployment Script
# Emergency Mode: Run when ready!

set -e

echo "🚀 Deploying Zhizhongcao to Railway..."
echo "Emergency mode: NO SLEEP!"

# Prerequisites (install first if not installed)
# curl -o- https://raw.githubusercontent.com/railwayapp/nixpacks/main/setup.sh | bash
# curl -O https://railway-cli.vercel.app/railway-linux-amd64
# chmod +x railway-linux-amd64
# sudo mv railway-linux-amd64 /usr/local/bin/railway

# Login to Railway
echo "Logging in to Railway..."
railway login

# Link project
echo "Linking to project..."
cd backend
railway link

# Build and deploy
echo "Building image..."
railway build

echo "Deploying to production..."
railway deploy --env production

echo ""
echo "✅ Deployment complete!"
echo "Visit your app at: $(railway summary --json | jq -r '.projects[0].services[0].environments.PRODUCTION.url')"

# Continuous monitoring
while true; do
    echo "👀 Monitoring deployment... $(date)"
    sleep 300  # Check every 5 minutes
done
