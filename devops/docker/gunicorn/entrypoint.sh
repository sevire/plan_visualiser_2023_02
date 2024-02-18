#!/usr/bin/env bash

cd /docker_app_root/plan_visualiser_2023_02 || exit

echo "Applying migrations..."
python manage.py migrate --noinput

echo "Collecting static..."
python manage.py collectstatic --noinput

# Add common data and initial users
echo "Adding common data..."
python manage.py add_common_data

# Reset pk sequence after adding common data with hard-coded pks.
echo "Updating primary key sequence after adding common data"
python manage.py update_pk_value

echo "Starting gunicorn..."
gunicorn plan_visualiser_2023_02.wsgi:application --bind 0.0.0.0:8000
