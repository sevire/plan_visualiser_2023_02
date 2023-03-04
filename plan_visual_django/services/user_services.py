"""
Service to manage information related to users.

Many of these services are related to current user logged in, which means the information is related to a
session.  Generally that information is encapsulated within the request object so often that is an input parameter.
"""
from django.contrib.auth import get_user_model
from django.http import HttpRequest


def get_current_user(request: HttpRequest, default_if_logged_out: bool):
    """
    If there is a current authenticated user then return the user, otherwise return None

    :param request:
    :return:
    """
    if request.user.is_authenticated:
        return request.user
    else:
        user_model = get_user_model()
        user = user_model.objects.get(username="default_user")
        return user