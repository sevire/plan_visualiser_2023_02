import os
from pathlib import Path
from django.contrib.messages import constants as messages

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = os.getenv('SECRET_KEY', 'dummy-secret-key-for-dev')

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'corsheaders',
    'rest_framework',
    'markdownify',
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

ROOT_URLCONF = "plan_visualiser_2023_02.urls"

# ------------------------------------------
# Logging Configuration
# ------------------------------------------
# Set logging levels from env variable if present but use defaults based on development if not.
LOGGING_LEVEL_H_CONSOLE = os.getenv('LOGGING_LEVEL_H_CONSOLE', 'INFO').upper()  # Handler/Console
LOGGING_LEVEL_H_FILE = os.getenv('LOGGING_LEVEL_H_FILE', 'INFO').upper()  # Handler/File
LOGGING_LEVEL_L_DJANGO = os.getenv('LOGGING_LEVEL_L_DJANGO', 'INFO').upper()  # Logger/Django
LOGGING_LEVEL_L_ROOT = os.getenv('LOGGING_LEVEL_L_ROOT', 'INFO').upper()  # Logger/Root

# Log folder configuration
LOG_FOLDER = os.path.join(BASE_DIR, "devops/logs")
os.makedirs(LOG_FOLDER, exist_ok=True)  # Ensure the directory exists

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
            "filename": os.path.join(BASE_DIR, "devops/logs/app_logs/debug.log"),
            "maxBytes": 1024*1024*2, # 2 MB - Keep size low enough so PyCharm log analyser can work
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
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

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
DATABASES = {}
AUTH_USER_MODEL = 'plan_visual_django.CustomUser'

AUTHENTICATION_BACKENDS = [
    'plan_visual_django.authentication.EmailOrUsernameBackend',
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LOGIN_REDIRECT_URL = '/'

EMAIL_HOST = ""
EMAIL_PORT = 465
EMAIL_USE_SSL = True

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

SHARED_DATA_USER_NAME = 'shared_data_user'  # Note has to match shared data user in initial_users within
DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000
CORS_ORIGIN_ALLOW_ALL = True
VERSION = "0.1.1"