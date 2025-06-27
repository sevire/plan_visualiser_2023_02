import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('DJANGO_DB_HOST', 'db'),
        'PORT': '5432',
    }
}

EMAIL_HOST = os.getenv('EMAIL_HOST', None)
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', None)
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', None)
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', None)
EMAIL_PORT = os.getenv('EMAIL_PORT', None)

print(f"EMAIL_HOST={EMAIL_HOST}")
print(f"EMAIL_USE_SSL={EMAIL_USE_SSL}")
print(f"EMAIL_HOST_USER={EMAIL_HOST_USER}")
print(f"EMAIL_HOST_PASSWORD={EMAIL_HOST_PASSWORD}")
print(f"EMAIL_PORT={EMAIL_PORT}")

STATIC_ROOT = "/static/"
MEDIA_ROOT = "/media/"
