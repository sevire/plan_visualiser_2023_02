import re
from dataclasses import dataclass
from enum import Enum


# class ShapeType(Enum):
#     RECTANGLE = 1
#     ROUNDED_RECTANGLE = 2
#     DIAMOND = 3
#     ISOSCELES_TRIANGLE = 4
#
#
class Unit(Enum):
    Cm = (1, "Centimeters", 1.0)
    In = (2, "Inches", 1/2.54)

    def __init__(self, index, long_name, cm_conversion_factor):
        self.index = index
        self.long_name = long_name
        self.cm_conversion = cm_conversion_factor


@dataclass
class DistanceMeasure:
    quantity: float = 0.0
    unit: Unit = None

    def as_unit(self, unit: Unit):
        return DistanceMeasure(self.quantity / self.unit.cm_conversion * unit.cm_conversion, unit)

    @classmethod
    def from_string(cls, string_measure):
        """
        The string must be of the form
            "nn.nnXX"
        where nn.nn is a numerical value representing a float
        and XX is the string value of the name of the unit (e.g. "Cm")

        An instance of DistanceMeasure is returned.
        """
        regex = re.compile(r'(\d+(\.\d*){0,1})([a-zA-Z]+)')
        parsed = regex.match(string_measure)
        groups = parsed.groups()

        value_string = groups[0]
        unit_string = groups[2]

        value = float(value_string)
        unit = Unit.__members__[unit_string]

        return cls(value, unit)

