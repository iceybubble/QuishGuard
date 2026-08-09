# Frontend Dockerfile - Simple static file server
FROM python:3.11-slim

WORKDIR /app

# Copy frontend files
COPY index.html .

# Expose port
EXPOSE 3000

# Simple Python HTTP server to serve the static files
CMD ["python", "-m", "http.server", "3000"]
