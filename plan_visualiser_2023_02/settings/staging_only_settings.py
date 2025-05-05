from .base_settings import *
from .common_staging_production_settings import *

DEBUG = False
ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['http://localhost', 'http://127.0.0.1', 'http://138.68.160.214']
