#!/bin/bash
set -e

# DB 마이그레이션
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running migrations..."
    python manage.py migrate
fi

# Collect static files
if [ "$RUN_COLLECTSTATIC" = "true" ]; then
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
fi

# Gunicorn 실행
exec gunicorn project.wsgi:application --bind 0.0.0.0:8000 --workers 3 --threads 2
