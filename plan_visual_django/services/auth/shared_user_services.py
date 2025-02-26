from django.contrib.auth import get_user_model
from django.conf import settings

def get_shared_user():
    User = get_user_model()
    shared_user = User.objects.get(username=settings.SHARED_DATA_USER_NAME)
    return shared_user