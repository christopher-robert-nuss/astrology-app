#!/bin/bash
PORT=${PORT:-8080}

# Kill any existing process on the port
echo "Checking port $PORT..."
sudo lsof -t -i:$PORT | xargs kill -9 2>/dev/null || true

echo "Starting FastAPI on port $PORT..."
uvicorn main:app --host 0.0.0.0 --port $PORT --reload