#!/bin/sh
set -e

echo "Waiting for database..."
sleep 5

echo "Running makemigrations..."
python manage.py makemigrations --noinput

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

exec "$@"
