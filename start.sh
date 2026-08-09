#!/bin/bash
# QuishGuard Startup Script
# Run this to start the application with Docker

set -e

echo "🛡️  Starting QuishGuard..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "   Get free API key: https://aistudio.google.com/app/apikeys"
    echo "   Create .env and add: GOOGLE_API_KEY=your-key-here"
    exit 1
fi

# Check if GOOGLE_API_KEY is set
if ! grep -q "GOOGLE_API_KEY=" .env || grep "GOOGLE_API_KEY=your-api-key-here" .env > /dev/null; then
    echo "❌ GOOGLE_API_KEY not configured in .env"
    echo "   Get free key: https://aistudio.google.com/app/apikeys"
    echo "   Edit .env and set your key"
    exit 1
fi

echo "✓ Configuration found"
echo ""

# Start services
echo "Starting Docker containers..."
docker-compose up

echo ""
echo "🎉 QuishGuard is running!"
echo "   Frontend: http://localhost:3000"
echo "   Backend: http://localhost:8000"
echo "   Health check: curl http://localhost:8000/health"
