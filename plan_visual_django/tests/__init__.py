import os

# Fallback to ensure `DJANGO_SETTINGS_MODULE` is correctly set
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plan_visualiser_2023_02.settings")
os.environ.setdefault("DJANGO_ENVIRONMENT", "development")