from unittest import TestCase
from ddt import ddt, unpack, data

from plan_visual_django.services.drawing.plan_visual_plotter import DistanceMeasure, Unit


@ddt
class TestMeasures(TestCase):
    test_conversion_data = [
        ("2.54Cm", "In", 2.54, 1.0),
        ("3Cm", "In", 3, 1.18110236),
        ("10In", "Cm", 10, 25.4),
    ]

    @data(*test_conversion_data)
    @unpack
    def test_unit_conversion(self, measure_string, to_unit_string, measure_value, converted_value):
        input_measure = DistanceMeasure.from_string(measure_string)
        output_unit = Unit.__members__[to_unit_string]
        output_measure = input_measure.as_unit(output_unit)

        self.assertAlmostEqual(measure_value, input_measure.quantity)
        self.assertAlmostEqual(converted_value, output_measure.quantity)

    test_data_from_string = [
        ("12.34Cm", 12.34, Unit.Cm),
        ("34In", 34, Unit.In),
    ]
    @data(*test_data_from_string)
    @unpack
    def test_from_string(self, string, exp_value, exp_unit):
        measure = DistanceMeasure.from_string(string)
        self.assertEqual(exp_value, measure.quantity)
        self.assertEqual(exp_unit, measure.unit)
