from dotenv import load_dotenv
from .base_settings import *

# Load email settings from .env file
dotenv_path = 'devops/env/.env.email.development'
load_dotenv(dotenv_path)

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

# Email settings
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


STATIC_ROOT = "/static/"