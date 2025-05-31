#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

cd /app/library_system


echo "Making migrations..."
python manage.py makemigrations

echo "Applying migrations..."
python manage.py migrate

echo "Starting server..."
# You can replace this with gunicorn or uvicorn if you want production-ready server
python manage.py runserver 0.0.0.0:8000
