from dotenv import load_dotenv
from .base_settings import *

# Load email settings from .env file
load_dotenv('devops/env/.env.email.development')

# Load other dev only env variables
load_dotenv('devops/env/.env.dev-local')

DEBUG = True

SECRET_KEY = "django-insecure-@!(&2yeohsybrswkzk#75vmj&w5c1l@!xftsbkvuzc+x4z$0yi"

ALLOWED_HOSTS = ['localhost', '127.0.0.1']
CSRF_TRUSTED_ORIGINS = ['http://localhost', 'http://127.0.0.1']

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # Enables the web interface
    ],
}

INTERNAL_IPS = ['127.0.0.1', '::1']


# Email settings
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'


STATIC_ROOT = "/static/"