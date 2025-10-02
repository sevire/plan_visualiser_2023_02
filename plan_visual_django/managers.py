"""
Custom model managers
"""
from django.db import models
from plan_visual_django.services.auth.shared_user_services import get_shared_user
from plan_visual_django.services.visual.model.visual_settings import VisualSettings


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


class PlanVisualManager(models.Manager):
    """
    Creating custom manager to help manage the complexities of creating a new visual, particularly
    that of managing defaults and adding child objects such as swimlanes and timelines.
    """
    def create_with_defaults(self, plan, **kwargs):
        """
        Create new PlanVisual instance with default values for missing fields.
        The function allows instance creation from various scenarios like UI forms or tests.
        """

        # Calculate defaults for fields which aren't specified
        defaults = VisualSettings.calculate_defaults_for_visual(plan, **kwargs)

        # Add defaults for missing fields
        for field, value in defaults.items():
            kwargs[field] = value

        # Create and return the instance
        from django.db import transaction
        with transaction.atomic():
            plan.visual_count += 1
            plan.save()
            return self.create(plan=plan, **kwargs)
