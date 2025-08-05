import os

print("Processing Django settings...")

CURRENT_ENVIRONMENT = os.getenv('DJANGO_ENVIRONMENT', 'development')

# Log the derived environment
print(f"DJANGO_ENVIRONMENT = {CURRENT_ENVIRONMENT}")
if CURRENT_ENVIRONMENT == 'production':
    print("Using PRODUCTION environment")
    from .production_only_settings import *
elif CURRENT_ENVIRONMENT == 'staging':
    print("Using STAGING environment")
    from .staging_only_settings import *
else:
    print("Using DEVELOPMENT environment")
    from .development_only_settings import *
