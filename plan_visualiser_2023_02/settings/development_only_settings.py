from .base_settings import *

DEBUG = True

SECRET_KEY = "django-insecure-@!(&2yeohsybrswkzk#75vmj&w5c1l@!xftsbkvuzc+x4z$0yi"

ALLOWED_HOSTS = ['localhost']
CSRF_TRUSTED_ORIGINS = ['http://localhost', 'http://127.0.0.1']

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

STATICFILES_DIRS = [BASE_DIR / "static"]
