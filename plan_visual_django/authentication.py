from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailOrUsernameBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in with either email or username.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = None

        if '@' in username:
            try:
                user = User.objects.get(email=username)
            except User.DoesNotExist:
                return None
        else:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return None

        if user and user.check_password(password):
            return user

        return None