from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from plan_visual_django.models import PlanVisual, Plan, PlotableStyle, DEFAULT_PLOTABLE_SHAPE_NAME, \
    DEFAULT_MILESTONE_PLOTABLE_SHAPE_NAME, Color, Font
from plan_visual_django.services.auth.user_services import CurrentUser

User = get_user_model()


class TestHasAccessToObject(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user_1 = User.objects.create_user(username="user1", password="password1", email="user1@test.com")
        self.user_2 = User.objects.create_user(username="user2", password="password2", email="user2@test.com")
        self.request_user_1 = self.factory.get("/")
        self.request_user_1.user = self.user_1
        self.request_user_2 = self.factory.get("/")
        self.request_user_2.user = self.user_2

        # Anonymous user request with session
        self.request_anon = self.factory.get("/")
        self.request_anon.session = self.client.session

        # Create a plan object owned by user_1
        self.plan_user_1 = Plan.objects.create(
            user=self.user_1,
            plan_name="Test Plan for User 1",
            file_name="test_plan_user1.xlsx"
        )

        # Anonymous session-based plan
        self.request_anon.session.create()
        self.plan_anon = Plan.objects.create(
            session_id=self.request_anon.session.session_key,
            plan_name="Test Plan for Anonymous",
            file_name="test_plan_anon.xlsx"
        )

    def utility_create_valid_plan_visual(self, plan):
        dummy_colour_object = Color.objects.create(
            name="Dummy Colour",
            user=self.user_1,  # Dummy value - not used
            red=0.234,
            green=0.234,
            blue=0.234,
            alpha=0.234,
        )
        # Resolve default styles (ensure these default styles exist in your database)
        dummy_style = PlotableStyle.objects.create(
            user=self.user_1,
            style_name="Dummy Style",
            fill_color=dummy_colour_object,
            line_color=dummy_colour_object,
            font_color=dummy_colour_object,
            line_thickness=5,
            font=Font.objects.create(font_name="dummy"),
            font_size=3,
        )

        # Create the PlanVisual object with all required fields
        plan_visual = PlanVisual.objects.create(
            plan=plan,
            name="Auto-Generated Visual",
            width=1200,
            max_height=800,
            include_title=False,
            track_height=20,
            track_gap=4,
            milestone_width=10,
            swimlane_gap=5,
            default_milestone_shape=DEFAULT_MILESTONE_PLOTABLE_SHAPE_NAME,
            default_activity_shape=DEFAULT_PLOTABLE_SHAPE_NAME,
            default_activity_plotable_style=dummy_style,
            default_milestone_plotable_style=dummy_style,
            default_swimlane_plotable_style=dummy_style,  # Example fallback: using the same as activity style
            default_timeline_plotable_style_odd=dummy_style,
            default_timeline_plotable_style_even=dummy_style,
        )
        return plan_visual

    def test_user_has_access_to_own_object(self):
        # User 1 should have access to their own plan
        current_user = CurrentUser(self.request_user_1)
        self.assertTrue(current_user.has_access_to_object(self.plan_user_1))

    def test_user_does_not_have_access_to_other_users_object(self):
        # User 2 should not have access to User 1's plan
        current_user = CurrentUser(self.request_user_2)
        self.assertFalse(current_user.has_access_to_object(self.plan_user_1))

    def test_anonymous_user_has_access_to_session_object(self):
        # Anonymous user should have access to their session-scoped plan
        current_user = CurrentUser(self.request_anon)
        self.assertTrue(current_user.has_access_to_object(self.plan_anon))
