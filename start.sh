#!/bin/sh
echo "=== STARTING PHILIA THRIFTS BOT ==="
echo "PORT env var: $PORT"
echo "Current directory: $(pwd)"
echo "Files in directory:"
ls -la
echo "Starting uvicorn on port ${PORT:-8080}..."
exec python main.py
