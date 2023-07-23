import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

from plan_visual_django.models import PlotableShapeType


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


class Renderer(ABC):
    """
    Generic abstract class which encapsulates the functionality to render a visual physically, e.g. to an HTML canvas
    during editing, or to write to a PPT file.

    The expected usage will be that a Canvas renderer will be implemented for editing the visual in real time, and then
    when the visual is ready for publishing, a different renderer (e.g. PowerPoint) will be invoked to render the same
    visual in PowerPoint.
    """
    @abstractmethod
    def plot_shape(
            self,
            plot_object,  # Will vary by medium, eg. Canvas, PPT slide object etc.
            shape_type: PlotableShapeType.PlotableShapeTypeName,
            top: DistanceMeasure,
            left: DistanceMeasure,
            width: DistanceMeasure,
            height: DistanceMeasure
    ):
        pass


class CanvasRenderer(Renderer):
    """
    A canvas renderer is special in that instead of working on a server side object such as a PPT slide, it needs
    to update the canvas on the visual page.

    This will be achieved by sending a RESTful message to the server with the details of changes to the canvas, and
    the client will update the canvas accordingly.

    NOTE: In the early version of this component, data about the whole visual will be sent to the web page which will
    plot.  That is it won't manage changes in real time (will always create the plot from scratch).
    """
    def __init__(self, canvas):
        self.canvas = canvas

    def plot_shape(self, canvas, shape_type, top, left, width, height):
        pass
