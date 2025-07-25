"""
Service to manage information related to users. (xxx-yyy-zzz-aaa)

Many of these services are related to current user logged in, which means the information is related to a
session.  Generally that information is encapsulated within the request object so often that is an input parameter.
"""
import logging
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from django.db import models

logger = logging.getLogger()

User = get_user_model()


def generate_username(email):
    """Generate a unique username based on email or a default prefix."""
    base_username = email.split('@')[0] if email else "user"
    username = base_username
    counter = 1

    # Ensure uniqueness of the username
    while User.objects.filter(username=username).exists():
        username = f"{base_username}_{counter}"
        counter += 1

    return username


class CurrentUser:
    """
    A reusable class for managing user authentication and permissions.
    Supports:
    - Model-level Django permissions (add, change, delete, view).
    - Object-level ownership checks (user or session-based).
    - Parent-child object relationships for inherited access.
    """

    def __init__(self, request: HttpRequest):
        self.request = request
        self.user = self._get_current_user()
        self.session_key = self._get_session_key() if self.is_anonymous() else None

    def _get_current_user(self):
        """Returns the current authenticated user or AnonymousUser."""
        return self.request.user if self.request.user.is_authenticated else AnonymousUser()

    def _get_session_key(self, create_flag=True):
        """
        Attempts to access the session key for the user.  If one not present then if create_flag is set then
        create one.

        Note create_flag has default of True as use_case where it would be False is when debuging.
        """
        if not self.request.session.session_key:
            logger.info("No session key yet.")
            if create_flag:
                logger.info("Creating new session key.")
                self.request.session.create()
            else:
                return None
        logger.info(f"Session key is {self.request.session.session_key}")
        return self.request.session.session_key

    def is_authenticated(self):
        return not isinstance(self.user, AnonymousUser)

    def is_anonymous(self):
        return isinstance(self.user, AnonymousUser)

    def get_identifier(self):
        """
        Returns the correct identifier for the user:
        - Returns `user.id` if authenticated.
        - Returns `session_key` if anonymous.
        - Also returns the correct attribute name for assignment.
        """
        if self.is_authenticated():
            return "user", self.user  # Correctly assigns to Plan.user
        return "session_id", self.session_key  # Correctly assigns to Plan.session_id

    def get_user_plans(self):
        """
        Returns all plans belonging to the current user.
        - Authenticated users: Query by user ID.
        - Anonymous users: Query by session key.
        """
        from plan_visual_django.models import Plan
        if self.is_authenticated():
            return Plan.objects.filter(user=self.user)
        return Plan.objects.filter(session_id=self.session_key)

    def get_num_user_plans(self):
        """
        Calculates the number of plans belonging to the current user.

        Plans will be stored either under a user name or a session key.  Depending upon current user
        get plans for this user.

        :return:
        """
        from plan_visual_django.models import Plan
        if self.is_authenticated():
            return Plan.objects.filter(user=self.user).count()
        return Plan.objects.filter(session_id=self.session_key).count()

    def generate_default_plan_name(self):
        """
        Calculates a default plan name for the plan based on user.
        :param user:
        :return:
        """
        user_part_of_name = self.get_user_display_name()
        num_existing_plans_for_user = self.get_num_user_plans()

        default_plan_name = f"Plan-{user_part_of_name}-{num_existing_plans_for_user+1:03}"

        return default_plan_name

    def get_user_display_name(self):
        """
        Gets username if authenticated else returns string of form Anon-xxxxx

        Note the name is used to help generate default names for plans etc and doesn't need
        to be unique.
        :return:
        """
        if self.is_authenticated():
            return self.user.username
        return f"Anon-{self.session_key[-5:]}"

    def has_access_to_object(self, obj):
        """
        Checks if the current user/session has access to a given model instance.

        :param obj: A Django model instance
        :return: Boolean (True if user has access, False otherwise)
        """

        # Case 1: Check for application-level models (not user-accessible)
        if hasattr(obj, "is_application_level") and obj.is_application_level:
            return False  # Not user-modifiable

        # Case 2: Direct user/session ownership
        if hasattr(obj, "user") and hasattr(obj, "session_id"):
            # We are checking whether either the user ids or the session keys are equal between object
            # and the user but if the user ids aren't equal then session ids both None isn't a match!
            if self.user == obj.user:
                return True
            elif self.session_key is not None and obj.session_id is not None and self.session_key == obj.session_id:
                return True
            else:
                return False  # Fail if either session_key or obj.session_id is None

        # Case 3: Follow parent-child relationships to find an owning model
        parent = self._get_parent_object(obj)
        if parent:
            return self.has_access_to_object(parent)  # Recursively check parent

        # Default: No access if no matching conditions are found
        return False

    def _get_parent_object(self, obj):
        """
        Tries to find a parent object that links to a user or session_id.
        """
        # If we pass an object in which doesn't have
        if hasattr(obj, "_meta"):
            for field in obj._meta.fields:
                if isinstance(field, models.ForeignKey):  # Only check foreign key relationships
                    related_obj = getattr(obj, field.name, None)
                    if related_obj:
                        return related_obj  # Return the first valid parent found
        return None


def get_current_user(request: HttpRequest, allow_anonymous: bool = False, default_if_logged_out: bool = False):
    """
    Returns the current authenticated user. If `allow_anonymous` is True, it allows
    AnonymousUser to be returned. If `default_if_logged_out` is True, it returns a default
    user when no authenticated user is found.

    :param request: HttpRequest object
    :param allow_anonymous: If True, return AnonymousUser instead of None.
    :param default_if_logged_out: If True, return a default user if no user is found.
    :return: User instance, AnonymousUser, or None.
    """
    if request.user.is_authenticated:
        return request.user  # Return the logged-in user

    if allow_anonymous:
        return request.user  # Keep AnonymousUser instead of replacing it

    if default_if_logged_out:
        user_model = get_user_model()
        return user_model.objects.order_by("id").first()  # Return the first available user

    return None  # No user available


def get_session_user_identifier(request):
    """Returns a session-based identifier for anonymous users."""
    if not request.session.session_key:
        request.session.create()  # Ensure session exists
    return f"session_{request.session.session_key}"