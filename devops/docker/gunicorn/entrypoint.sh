#!/usr/bin/env bash

echo "
=================================================================
||                                                             ||
||                 ENTRYPOINT.SH STARTING                      ||
||                 $(date '+%Y-%m-%d %H:%M:%S')                         ||
||                                                             ||
=================================================================
"

echo "Echoing current directory"
pwd

echo "
=================================================================
|| Applying migrations...                                      ||
=================================================================
"

python manage.py migrate --noinput

echo "
=================================================================
|| Collecting static...                                        ||
=================================================================
"

python manage.py collectstatic --noinput

# Add common data and initial users
echo "
=================================================================
|| Adding common data...                                       ||
=================================================================
"
python manage.py add_common_data

echo "
=================================================================
|| Updating primary key sequence after adding common data...   ||
=================================================================
"
python manage.py update_pk_value

echo "
=================================================================
||                                                             ||
||                 ENTRYPOINT.SH STARTING GUNICORN (LAST TASK) ||
||                 $(date '+%Y-%m-%d %H:%M:%S')                         ||
||                                                             ||
=================================================================
"
gunicorn plan_visualiser_2023_02.wsgi:application --bind 0.0.0.0:8000

