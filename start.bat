@echo off
REM QuishGuard Startup Script for Windows
REM Run this to start the application with Docker

echo 🛡️  Starting QuishGuard...
echo.

REM Check if .env file exists
if not exist .env (
    echo ❌ .env file not found!
    echo    Get free API key: https://aistudio.google.com/app/apikeys
    echo    Create .env and add: GOOGLE_API_KEY=your-key-here
    exit /b 1
)

echo ✓ Configuration found
echo.

REM Start services
echo Starting Docker containers...
docker-compose up

echo.
echo 🎉 QuishGuard is running!
echo    Frontend: http://localhost:3000
echo    Backend: http://localhost:8000
echo    Health check: curl http://localhost:8000/health
