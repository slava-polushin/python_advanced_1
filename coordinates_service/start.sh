#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

# Start the FastAPI application
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8001}
