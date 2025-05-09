import os

print("Checking DJANGO_SETTINGS_MODULE...")
print(f"DJANGO_SETTINGS_MODULE (before): {os.getenv('DJANGO_SETTINGS_MODULE')}")

environment = os.getenv('DJANGO_ENVIRONMENT', 'development')

# Log the derived environment
print(f"DJANGO_ENVIRONMENT = {environment}")
if environment == 'production':
    print("Using PRODUCTION environment")
    from .production_only_settings import *
elif environment == 'staging':
    print("Using STAGING environment")
    from .staging_only_settings import *
else:
    print("Using DEVELOPMENT environment")
    from .development_only_settings import *

print(f"DJANGO_SETTINGS_MODULE (after): {os.getenv('DJANGO_SETTINGS_MODULE')}")