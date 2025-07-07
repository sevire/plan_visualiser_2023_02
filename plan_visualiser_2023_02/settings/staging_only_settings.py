from .base_settings import *
from .common_staging_production_settings import *

DEBUG = False

# Set default domain for sending password reset emails etc.
DEFAULT_DOMAIN = "138.68.160.214"
ALLOWED_HOSTS = ['localhost', '127.0.0.1', DEFAULT_DOMAIN]
CSRF_TRUSTED_ORIGINS = ['http://localhost', 'http://127.0.0.1', 'http://'+DEFAULT_DOMAIN]
