#!/bin/sh

set -e

echo "========================================"
echo "Starting Dokploy Learning Application"
echo "========================================"

echo "Running database migrations..."

flask --app app db upgrade

echo "Database migrations completed successfully."

echo "Starting Gunicorn..."

exec gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 2 \
    --timeout 60 \
    app:app
