"""
Django settings for plan_visualiser_2023_02 project.

Generated by 'django-admin startproject' using Django 4.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os
from pathlib import Path
from django.contrib.messages import constants as messages
import logging

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# Find out whether we are working in a development or production environment
# by checking the environment variable DJANGO_ENVIRONMENT.
# If it is equal to 'production', then we are in production mode.
# Otherwise, we are in development mode.
DJANGO_ENVIRONMENT = os.getenv('DJANGO_ENVIRONMENT')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# Read other env variables here (so they are all in one place)

print(f"DJANGO_ENVIRONMENT = {DJANGO_ENVIRONMENT}")
logging.info(f"DJANGO_ENVIRONMENT = {DJANGO_ENVIRONMENT}")
if DJANGO_ENVIRONMENT == 'production':
    logging.info('Using PRODUCTION environment')
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = False

    # Set logging levels from env variable if present but use defaults based on production if not.
    LOGGING_LEVEL_H_CONSOLE = os.getenv('LOGGING_LEVEL_H_CONSOLE', 'INFO').upper()  # Handler/Console
    LOGGING_LEVEL_H_FILE = os.getenv('LOGGING_LEVEL_H_FILE', 'INFO').upper()  # Handler/File
    LOGGING_LEVEL_L_DJANGO = os.getenv('LOGGING_LEVEL_L_DJANGO', 'INFO').upper()  # Logger/Django
    LOGGING_LEVEL_L_ROOT = os.getenv('LOGGING_LEVEL_L_ROOT', 'INFO').upper()  # Logger/Root

    ALLOWED_HOSTS = ['planononepage.com', '206.189.127.49']
    CSRF_TRUSTED_ORIGINS = ['http://localhost', 'http://127.0.0.1', 'http://138.68.160.214', 'https://planononepage.com', 'https://www.planononepage.com']
elif DJANGO_ENVIRONMENT == 'staging':
    logging.info('Using STAGING environment')
    SECRET_KEY = os.getenv('SECRET_KEY')
    DEBUG = False

    # Set logging levels from env variable if present but use defaults based on production if not.
    LOGGING_LEVEL_H_CONSOLE = os.getenv('LOGGING_LEVEL_H_CONSOLE', 'INFO').upper()  # Handler/Console
    LOGGING_LEVEL_H_FILE = os.getenv('LOGGING_LEVEL_H_FILE', 'INFO').upper()  # Handler/File
    LOGGING_LEVEL_L_DJANGO = os.getenv('LOGGING_LEVEL_L_DJANGO', 'INFO').upper()  # Logger/Django
    LOGGING_LEVEL_L_ROOT = os.getenv('LOGGING_LEVEL_L_ROOT', 'INFO').upper()  # Logger/Root

    ALLOWED_HOSTS = ['*']
    CSRF_TRUSTED_ORIGINS = ['http://localhost', 'http://127.0.0.1', 'http://138.68.160.214']
else:
    print('Using DEVELOPMENT environment')
    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = "django-insecure-@!(&2yeohsybrswkzk#75vmj&w5c1l@!xftsbkvuzc+x4z$0yi"
    DEBUG = True

    # Set logging levels from env variable if present but use defaults based on development if not.
    LOGGING_LEVEL_H_CONSOLE = os.getenv('LOGGING_LEVEL_H_CONSOLE', 'INFO').upper()  # Handler/Console
    LOGGING_LEVEL_H_FILE = os.getenv('LOGGING_LEVEL_H_FILE', 'DEBUG').upper()  # Handler/File
    LOGGING_LEVEL_L_DJANGO = os.getenv('LOGGING_LEVEL_L_DJANGO', 'DEBUG').upper()  # Logger/Django
    LOGGING_LEVEL_L_ROOT = os.getenv('LOGGING_LEVEL_L_ROOT', 'DEBUG').upper()  # Logger/Root

    ALLOWED_HOSTS = ['*']
    CSRF_TRUSTED_ORIGINS = ['http://localhost', 'http://127.0.0.1', 'http://138.68.160.214']

# Modified to support custom user model
AUTH_USER_MODEL = 'plan_visual_django.CustomUser'

AUTHENTICATION_BACKENDS = [
    'plan_visual_django.authentication.EmailOrUsernameBackend',  # Custom backend
]
# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'corsheaders',
    'rest_framework',
    'plan_visual_django.apps.PlanVisualDjangoConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ------------------------------------------
# Session Configuration
# ------------------------------------------

# Sessions backed by DB is default value but set it explicitly for clarity.
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7 * 2  # 2 weeks
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True


# ------------------------------------------
# Logging Configuration
# ------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname:6} {asctime} {name} ({filename}:{lineno}): {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": LOGGING_LEVEL_H_CONSOLE,
            "class": "logging.StreamHandler",
            "formatter": "verbose"
        },
        "file": {
            "level": LOGGING_LEVEL_H_FILE,
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(BASE_DIR, "logs/debug.log"),
            "maxBytes": 1024*1024*5, # 5 MB
            "backupCount": 5,
            "formatter": "verbose"
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "DEBUG",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": LOGGING_LEVEL_L_DJANGO,
            "propagate": False,
        },
        "root": {
            "handlers": ["console", "file"],
            "level": LOGGING_LEVEL_L_ROOT,
            "propagate": False
        },
        'django.middleware': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

CORS_ORIGIN_ALLOW_ALL = True  # ToDo: Set CORS correctly for live - this is for testing against separate UI app
ROOT_URLCONF = "plan_visualiser_2023_02.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "plan_visualiser_2023_02.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

if DJANGO_ENVIRONMENT == 'production' or DJANGO_ENVIRONMENT == 'staging':
    print("Using PostgreSQL database in staging/production")
    # Use the PostgreSQL database in production
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('POSTGRES_NAME'),
            'USER': os.getenv('POSTGRES_USER'),
            'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
            'HOST': 'db',
            'PORT': '5432',
        }
    }
else:
    print("Using SQLite database in development")
    # Use the SQLite database in development
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-secondary',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "/static/"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
if DJANGO_ENVIRONMENT == 'production':
    STATIC_ROOT = "/static/"
    MEDIA_ROOT = "/media/"
elif DJANGO_ENVIRONMENT == 'staging':
    STATIC_ROOT = "/static/"
    MEDIA_ROOT = "/media/"
else:
    STATICFILES_DIRS = [BASE_DIR / "static"]

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Redirect to home URL after login (Default redirects to /accounts/profile/)
LOGIN_REDIRECT_URL = '/'

# Email settings, mostly to support resetting of passwords for users
EMAIL_HOST = ""
EMAIL_PORT = 465
EMAIL_USE_SSL = True

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SHARED_DATA_USER_NAME = 'shared_data_user'  # Note has to match shared data user in initial_users within
# add_common_data command
# ToDo: Remove duplication of shared_data_user name between settings and add_common_data command
SHARED_DATA_USER_EMAIL = 'tbg-pv-automateddatauser@genonline.co.uk'
SHARED_DATA_PREFIX = "AAA"

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000

VERSION = "0.1.0"
