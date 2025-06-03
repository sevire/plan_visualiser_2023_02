from ddt import ddt, data, unpack
from django.test import TestCase

from api.v1.model.visual.plotable_shape.serializer import PlotableShapeSerializer
from plan_visual_django.services.visual.model.plotable_shapes import PlotableShapeName, PlotableShapeObjectRectangle

"""
Tests to confirm that PlotableShapeObject behaves as expected for different shapes and scenarios
"""

class TestPlotableShapeName(TestCase):
    def test_plotable_shape_serialiser(self):
        choices = PlotableShapeName.choices

        serialiser_1 = PlotableShapeSerializer(data=PlotableShapeName.ROUNDED_RECTANGLE)
        serialiser_2 = PlotableShapeSerializer(many=True)
        data_1 = serialiser_1.data
        data_2 = serialiser_2.data
        pass

    def test_plotable_shape_name(self):
        """
        Just tests the mechanics of the PlotableShapeName class as it is an extension of TextChoices and there are
        a few nuances to check are working
        :return:
        """
        rectangle = PlotableShapeName.RECTANGLE

        clazz = rectangle.shape_object_class
        self.assertEqual(clazz, PlotableShapeObjectRectangle)

        rectangle_1 = PlotableShapeName.get_by_value("RECTANGLE")
        self.assertEqual("Rectangle", rectangle_1.label)
        pass


@ddt
class TestVisualShapes(TestCase):
    @data(
        (PlotableShapeName.RECTANGLE, 10, 8, {}, {}),
        (PlotableShapeName.ROUNDED_RECTANGLE, 11, 9, {}, {"corner_radius_value": 0.3 * 9}),
        (PlotableShapeName.ROUNDED_RECTANGLE, 50, 12, {'corner_radius_value': 3}, {'corner_radius_value': 3}),
        (PlotableShapeName.ROUNDED_RECTANGLE, 100, 4, {'corner_radius_percentage': 0.4}, {'corner_radius_value': 1.6}),
        (PlotableShapeName.DIAMOND, 30, 200, {}, {}),
        (PlotableShapeName.ISOSCELES_TRIANGLE, 1000, 2, {}, {}),
        (PlotableShapeName.BULLET, 300, 100, {}, {"corner_radius_value": 0.5 * 100}),
    )
    @unpack
    def test_visual_shapes(self, shape_name: PlotableShapeName, width: float, height: float, input_other_attributes, expected_other_attributes):
        shape = shape_name.shape_object_class(width=width, height=height, **input_other_attributes)

        with self.subTest("Check width"):
            self.assertEqual(shape.attributes['width'], width)
        with self.subTest("Check height"):
            self.assertEqual(shape.attributes['height'], height)
        if expected_other_attributes:
            for expected_attribute_name, expected_attribute_value in expected_other_attributes.items():
                with self.subTest(f"Check attribute {expected_attribute_name}"):
                    self.assertEqual(shape.attributes[expected_attribute_name], expected_attribute_value)
            # Check that there aren't any additional keys other than those expected
            with self.subTest("Check that there aren't any additional keys other than width and height"):
                self.assertEqual(set(shape.attributes.keys()) - set(expected_other_attributes.keys()), {"width", "height"})
