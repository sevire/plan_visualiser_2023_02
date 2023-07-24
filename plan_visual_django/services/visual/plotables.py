from abc import ABC, abstractmethod

from plan_visual_django.models import PlotableShapeType, PlotableStyle, VisualActivity


class Plotable(ABC):
    """
    Abstract class which supports an object which can be represented visually as an object on a diagram. Agnostic of how
    the visual will be actually physically plotted.  Separate components will be added through composition or
    sub-classing in order to carry out or support the actual drawing of the object.
    """
    def __init__(self, shape: PlotableShapeType.PlotableShapeTypeName):
        """
        All objects will need at least a shape.

        :param shape:
        """
        self.shape = shape

    @abstractmethod
    def plot(self):
        pass

    def get_dimensions(self):
        """
        Although a plotable shape can be an irregular shape which doesn't have four points neatly arranged in a
        rectangle, ultimately the visual will be plotted within a rectangular space, and so to ensure that objects are
        scaled correctly to fit within the target space, we need to be able to find the enclosing rectangle for each
        plotable shape, and in turn each plotable collection.

        :return: (left, top, width, height, right, bottom)
        """
        return \
            self.get_top(), self.get_left(), self.get_width(), self.get_height(), \
            self.get_left() + self.get_width(), self.get_top() + self.get_height()


    @abstractmethod
    def get_left(self):
        """
        A plotable can be any shape which is representable by a collection of points.  However it will be necessary
        for some operations to think of a plotable as being contained within a surrounding rectangle, which will have
        a left edge, a top, a width and a height, so every plotable must be able to calculated these properties.

        Many plotables will be specified this way in any case but for irregular shapes it may be less straightforward.
        :return: float representing the x coordinate of a hyperthetical vertical line which just touches the leftmost
        point of the plotable shape.
        """
        pass

    @abstractmethod
    def get_top(self):
        pass

    @abstractmethod
    def get_width(self):
        """
        Calculate width of enclosing rectangle which is basically minimum left edge and maximum right edge.
        :return:
        """
        pass

    @abstractmethod
    def get_height(self):
        pass

    @abstractmethod
    def get_right(self):
        """
        Calculate rightmost edge of enclosing rectangle, which is (usually) the max of left + width for each plotable

        :return:
        """


class RectangleBasedPlotable(Plotable):
    """
    This class implements a family of plotable shapes which use a rectangular frame as a way of defining
    how the shape should be plotted.  The position and size of the shape are defined by top, left, width
    and height properties, but within that many shapes can be plotted, such as rectangles, rounded rectangles,
    triangles etc.

    There may be additional information required to represent varients to the shape, such as the radius of the
    rounded corners on a rounded rectangle, and these will be represented by subclassing this class to add
    shape specific behaviour.
    """

    def __init__(
            self,
            shape: PlotableShapeType.PlotableShapeTypeName,
            top: float,
            left: float,
            width: float,
            height: float,
            format: PlotableStyle,
            text_vertical_alignment: VisualActivity.VerticalAlignment,
            text_flow: VisualActivity.TextFlow,
            text: str,
            external_text_flag: bool
    ):
        super().__init__(shape)

        self.text_vertical_alignment = text_vertical_alignment
        self.top = top
        self.left = left
        self.width = width
        self.height = height
        self.shape = shape
        self.format = format
        self.text_flow = text_flow
        self.text = text
        self.external_text_flag = external_text_flag

    def get_top(self):
        return self.top

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_left(self):
        return self.left

    def get_right(self):
        return self.left + self.width

    def get_bottom(self):
        return self.top + self.height

    def plot(self):
        pass


class PlotableFactory:
    plotable_factory_dispatch_table = {
        PlotableShapeType.PlotableShapeTypeName.RECTANGLE: RectangleBasedPlotable,
        PlotableShapeType.PlotableShapeTypeName.ROUNDED_RECTANGLE: RectangleBasedPlotable,
        PlotableShapeType.PlotableShapeTypeName.DIAMOND: RectangleBasedPlotable,
        PlotableShapeType.PlotableShapeTypeName.ISOSCELES_TRIANGLE: RectangleBasedPlotable
    }

    @classmethod
    def get_plotable(cls, shape: PlotableShapeType.PlotableShapeTypeName, **kwargs):
        """
        Decides which subclass of plotable is required based on which shape is to be plotted.

        :param shape:

        :return:
        """
        class_to_use = cls.plotable_factory_dispatch_table[shape]
        return class_to_use(shape, **kwargs)


