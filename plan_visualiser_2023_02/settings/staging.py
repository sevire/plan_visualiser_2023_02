from .base import *
from .common_staging_production import *

DEBUG = False
ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['http://staging.example.com']
