from .base_settings import *
from .common_staging_production_settings import *

DEBUG = False

# Set default domain for sending password reset emails etc.
DEFAULT_DOMAIN = "206.189.127.49"
ALLOWED_HOSTS = ['planononepage.com', DEFAULT_DOMAIN]
CSRF_TRUSTED_ORIGINS = ['https://planononepage.com', 'https://www.planononepage.com']
