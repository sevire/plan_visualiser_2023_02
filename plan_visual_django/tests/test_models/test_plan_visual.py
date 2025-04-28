import os

from django.test import TestCase
from plan_visual_django.models import PlanVisual, Plan, PlotableStyle, CustomUser, Color, Font
from plan_visual_django.services.visual.model.plotable_shapes import PlotableShapeName
from test_configuration import test_data_base_folder, test_fixtures_folder
from utilities import create_default_styles_for_tests


class TestPlanVisual(TestCase):
    fixtures = [
        os.path.join(test_data_base_folder, test_fixtures_folder, 'auth_test_fixtures.json'),
        os.path.join(test_data_base_folder, test_fixtures_folder, 'test_fixtures.json')
    ]
    def setUp(self):
        """
        We need to add plotable styles of the right name so that the default values can be used
        when creating visuals.
        :return:
        """
        User = CustomUser
        user_to_use = User.objects.get(pk=1)
        color_to_use = Color.objects.get(pk=1)

        create_default_styles_for_tests(color_to_use, user_to_use)

    def test_create_plan_visual_with_defaults(self):
        """
        Check that visuals created with different combinations of supplied attributes are correctly
        created with defaults for remaining attributes.
        :return:
        """
        plotable_style_to_use = PlotableStyle.objects.get(pk=1)

        # Test driver table - visual attribute name: (value when not default, whether to use in default test, default value expected)
        attributes_to_test = {
            "name": ("plan_visual_default_test_xx", True, "Plan 1-Visual-03"),  # There are 2 visuals in text fixtures so this is 3rd
            "width": (123, True, 1200),
            "max_height": (234, True, 800),
            "include_title": (True, True, False),
            "track_height": (25, True, 20),
            "track_gap": (12, True, 4),
            "milestone_width": (90, True, 10),
            "swimlane_gap": (68, True, 5),
            "default_milestone_shape": (PlotableShapeName.ROUNDED_RECTANGLE.value, True, PlotableShapeName.DIAMOND.value),
            "default_activity_shape": (PlotableShapeName.ISOSCELES_TRIANGLE.value, True, PlotableShapeName.RECTANGLE.value),
            "default_activity_plotable_style": (plotable_style_to_use, True, "theme-01-001-activities-01"),
            "default_milestone_plotable_style": (plotable_style_to_use, True, "theme-01-004-milestones-01"),
            "default_swimlane_plotable_style": (plotable_style_to_use, True, "theme-01-006-swimlanes-01"),
            "default_timeline_plotable_style_odd": (plotable_style_to_use, True, "theme-01-008-timelines-01"),
            "default_timeline_plotable_style_even": (plotable_style_to_use, True, "theme-01-009-timelines-02"),
        }

        plan = Plan.objects.get(pk=2)

        # This loop tests each attribute's default value by creating a PlanVisual with all attributes except the current one.
        # For each attribute, it creates a visual with all other attributes provided, then verifies that:
        # 1. All provided attributes are correctly assigned their values
        # 2. The missing attribute is correctly assigned its default value
        for attribute_index, (attribute_name, (attribute_value, use_in_default_test, expected_default_value)) in enumerate(attributes_to_test.items()):
            with self.subTest(f"Checking default for {attribute_name}: {attribute_value}, {use_in_default_test}, {expected_default_value}"):


                # We set the value of all attributes apart from the current default attribute
                if use_in_default_test:
                    # Remove default from attributes and pass remainder into creation of visual so that only the current
                    # attribute being iterated gets a default value
                    attributes_to_test_copy = attributes_to_test.copy()
                    del attributes_to_test_copy[attribute_name]

                    # If the attribute default we are testing isn't 'name', then we need to adjust the value as otherwise
                    # when we create the visual for the second non-default name attribute, the unique constraint for visual
                    # and name will be violated.
                    if attribute_name != "name":
                        name, x, y = attributes_to_test_copy['name']
                        new_name = name.replace("xx", f"{attribute_index:02d}")
                        attributes_to_test_copy['name'] = (new_name, x, y)

                    visual_provided_args = {name: provided_value for name, (provided_value, _, _) in attributes_to_test_copy.items()}

                    # We are creating a new visual with all attributes provided other than the one we are testing, so
                    # we can check that the correct default value is calculated/assigned for the missing attribute.
                    visual = PlanVisual.objects.create_with_defaults(
                        plan=plan,
                        **visual_provided_args
                    )
                    # Check that non-default attributes correctly assigned value
                    for test_attribute_name, (test_provided_attribute_value, test_use_in_default_test, _) in attributes_to_test_copy.items():
                        with self.subTest(f"Testing {test_attribute_name}"):
                            self.assertEqual(getattr(visual, test_attribute_name), test_provided_attribute_value)

                    # Now test that missing attribute was assigned correct default
                    with self.subTest(f"Testing {attribute_name}"):
                        # ToDo: This is a bit of a hack!
                        # If the attribute is one of the plotable styles then we need to get the name of the style and
                        # check against that.
                        if attribute_name in [
                            "default_activity_plotable_style",
                            "default_milestone_plotable_style",
                            "default_swimlane_plotable_style",
                            "default_timeline_plotable_style_odd",
                            "default_timeline_plotable_style_even"
                        ]:
                            style: PlotableStyle = getattr(visual, attribute_name)
                            visual_attribute_value = style.style_name
                            self.assertEqual(visual_attribute_value, expected_default_value)
                        else:
                            self.assertEqual(getattr(visual, attribute_name), expected_default_value)
