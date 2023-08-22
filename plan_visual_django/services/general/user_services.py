"""
Service to manage information related to users.

Many of these services are related to current user logged in, which means the information is related to a
session.  Generally that information is encapsulated within the request object so often that is an input parameter.
"""
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.http import HttpRequest

from plan_visual_django.models import Plan, PlanVisual


def get_current_user(request: HttpRequest, default_if_logged_out: bool=False):
    """
    If there is a current authenticated user then return the user, otherwise return None

    :param default_if_logged_out:
    :param request:
    :return:
    """
    if request.user.is_authenticated:
        return request.user
    elif default_if_logged_out:
        user_model = get_user_model()
        user = user_model.objects.get(username="default_user")
        return user
    else:
        return None


def can_access_plan(user:User, plan_id: Plan):
    """
    Return true if the user can access the plan, otherwise return false

    :param user:
    :param plan:
    :return:
    """
    try:
        plan = Plan.objects.get(id=plan_id)
    except Plan.DoesNotExist:
        return False
    if user.is_superuser:
        return True
    elif plan.user == user:
        return True
    else:
        return False


def can_access_visual(user, visual_id:PlanVisual):
    """
    Return true if the user can access the visual, otherwise return false

    :param visual_id:
    :param user:
    :return:
    """
    try:
        visual = PlanVisual.objects.get(id=visual_id)
    except PlanVisual.DoesNotExist:
        return False
    if user.is_superuser:
        return True
    elif visual.plan.user == user:
        return True
    else:
        return False
