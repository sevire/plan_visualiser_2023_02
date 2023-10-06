#!/usr/bin/env bash

python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py makesuperuser
python manage.py add_common_data

gunicorn plan_visualiser_2023_02.wsgi:application --bind 0.0.0.0:8000
