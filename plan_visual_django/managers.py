"""
Custom model managers
"""
from django.db import models

from plan_visual_django.services.auth.shared_user_services import get_shared_user


class PlotableStyleManager(models.Manager):
    def for_user(self, user, include_shared=True):
        """
        Returns a queryset of styles related to a given user.  If include_shared is True, then shared styles are also
        included, which will be the usual case.

        :param user:
        :param include_shared:
        :return:
        """
        allowed_users = []
        if user and hasattr(user, 'is_authenticated') and user.is_authenticated:
            allowed_users.append(user)
        if include_shared:
            shared_user = get_shared_user()
            allowed_users.append(shared_user)
        return self.filter(user__in=allowed_users)