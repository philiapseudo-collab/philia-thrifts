#!/bin/sh
echo "PORT env var: $PORT"
PORT=${PORT:-8080}
echo "Using port: $PORT"
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
