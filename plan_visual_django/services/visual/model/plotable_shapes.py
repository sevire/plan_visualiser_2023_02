from abc import ABC, abstractmethod
from enum import Enum

from django.db import models

DEFAULT_CORNER_RADIUS_PERCENTAGE = 0.3

"""
Introduced in order to remove need for shape information to be held in the database, as this added a level of complexity
without any benefit as shapes need code associated with them to plot them.
"""

class PlotableShapeObject:
    def __init__(self, **attributes):
        """Master initializer for attributes common to all shapes."""
        self.attributes = attributes


class PlotableShapeObjectRectangle(PlotableShapeObject):
    # Associated shape name
    def __init__(self, width: float, height: float):
        super().__init__(width=width, height=height)


class PlotableShapeObjectDiamond(PlotableShapeObject):
    def __init__(self, width: float, height: float):
        super().__init__(width=width, height=height)


class PlotableShapeObjectIsosceles(PlotableShapeObject):
    def __init__(self, width: float, height: float):
        super().__init__(width=width, height=height)


class PlotableShapeObjectRoundedRectangle(PlotableShapeObject):
    """
    Rounded rectangle has a corner radius property which can be either a set value (in the abstract unit of the visual)
    or be a percentage of the height of the shape.  This allows flexibility in how the shape is plotted
    but note that in most cases it is expected that the default percentage will be used.

    Note that corner_radius_percentage is only used to allow the corner radius to be dependent upon the height of
    the shape.  It isn't needed to render the shape itself, but is used to calculate the corner radius value.
    """
    def __init__(
            self,
            width: float,
            height: float,
            corner_radius_value: float = None,
            corner_radius_percentage: float = DEFAULT_CORNER_RADIUS_PERCENTAGE  # Found by trial and error to be a good default value
    ):
        super().__init__(width=width, height=height)

        if corner_radius_value is not None:
            self.attributes['corner_radius_value'] = corner_radius_value
        else:
            self.attributes['corner_radius_value'] = height * corner_radius_percentage


class PlotableShapeObjectBullet(PlotableShapeObjectRoundedRectangle):
    def __init__(self, width: float, height: float):
        super().__init__(width, height, corner_radius_percentage=0.5)







# Enum-like definition
class PlotableShapeName(Enum):
    RECTANGLE = 1, "RECTANGLE", "Rectangle", PlotableShapeObjectRectangle
    ROUNDED_RECTANGLE = 2, "ROUNDED_RECTANGLE", "Rounded Rectangle", PlotableShapeObjectRoundedRectangle
    BULLET = 3, "BULLET", "Bullet", PlotableShapeObjectBullet
    DIAMOND = 4, "DIAMOND", "Diamond", PlotableShapeObjectDiamond
    ISOSCELES_TRIANGLE = 5, "ISOSCELES", "Isosceles Triangle", PlotableShapeObjectIsosceles

    def __init__(self, id, value, label, cls):
        self._id = id
        self._value_ = value  # stored string value
        self.label = label
        self.cls = cls        # associated behaviour class

    @property
    def id(self):
        return self._id

    @classmethod
    def choices(cls):
        return [(member.value, member.label) for member in cls]

    @classmethod
    def get_by_id(cls, id):
        for member in cls:
            if member.id == id:
                return member
        raise ValueError(f"No shape with id={id}")

    @classmethod
    def get_by_value(cls, value):
        return cls[value]

    @property
    def shape_object_class(self):
        """Instantiates the behaviour class for a given shape value."""
        return self.cls





# To be deleted as soon as I'm sure the replacement (above) is right.
class xPlotableShapeName(models.TextChoices):
    """
    Enum representing plotable shape names, with references to their corresponding classes.
    """
    RECTANGLE = "RECTANGLE", "Rectangle"
    ROUNDED_RECTANGLE = "ROUNDED_RECTANGLE", "Rounded Rectangle"
    BULLET = "BULLET", "Bullet"
    DIAMOND = "DIAMOND", "Diamond"
    ISOSCELES_TRIANGLE = "ISOSCELES", "Isosceles Triangle"

    # Use a method to define and return the mapping
    @classmethod
    def _get_shape_classes(cls):
        """
        Class-level method to return the mapping of enum values to shape classes.
        This is a bit of a hack to overcome constraints placed by definition of TextChoices.  I'd prefer to add
        the class reference to each member as part of its declaration but that creates conflicts.
        """
        return {
            cls.RECTANGLE.value: PlotableShapeObjectRectangle,
            cls.ROUNDED_RECTANGLE.value: PlotableShapeObjectRoundedRectangle,
            cls.BULLET.value: PlotableShapeObjectBullet,
            cls.DIAMOND.value: PlotableShapeObjectDiamond,
            cls.ISOSCELES_TRIANGLE.value: PlotableShapeObjectIsosceles,
        }

    @property
    def shape_object_class(self):
        """
        Accessor for the associated PlotableShapeObject subclass.
        Returns the actual class reference.
        """
        # Explicitly call the class-level method
        shape_classes = self._get_shape_classes()
        cls = shape_classes.get(self.value)
        if cls is None:
            raise ValueError(f"No associated shape class found for `{self.label}`.")
        return cls
