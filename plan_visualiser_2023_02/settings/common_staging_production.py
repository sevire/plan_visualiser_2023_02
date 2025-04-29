import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB_NAME'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('DJANGO_DB_HOST', 'db'),
        'PORT': '5432',
    }
}

STATIC_ROOT = "/static/"
MEDIA_ROOT = "/media/"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname:6} {asctime} {name} ({filename}:{lineno}): {message}",
            "style": "{",
        },
    }
}