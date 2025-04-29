import os

print("Checking which settings to use...")

print(f"DJANGO_ENVIRONMENT = {os.getenv('DJANGO_ENVIRONMENT')}")
environment = os.getenv('DJANGO_ENVIRONMENT', 'development')

if environment == 'production':
    print('Using PRODUCTION environment')
    from .production import *
elif environment == 'staging':
    print('Using STAGING environment')
    from .staging import *
else:
    print('Using DEVELOPMENT environment')
    from .development import *