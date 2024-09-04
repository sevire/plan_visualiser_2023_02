from abc import ABC, abstractmethod


class Plotable(ABC):
    """
    Abstract class which supports an object which can be represented visually as an object on a diagram. Agnostic of how
    the visual will be actually physically plotted.  Separate components will be added through composition or
    sub-classing in order to carry out or support the actual drawing of the object.
    """

    def __init__(self, shape, ):
        """
        All objects will need at least a shape.

        :param shape:
        """
        self.shape = shape

    def __str__(self):
        return f"t:{self.get_top()},l:{self.get_left()},w:{self.get_width()},h:{self.get_height()}"

    @abstractmethod
    def render(self, renderer):
        pass

    def get_dimensions(self):
        """
        Although a plotable shape can be an irregular shape which doesn't have four points neatly arranged in a
        rectangle, ultimately the visual will be plotted within a rectangular space, and so to ensure that objects are
        scaled correctly to fit within the target space, we need to be able to find the enclosing rectangle for each
        plotable shape, and in turn each plotable collection.

        :return: (top, left, width, height, right, bottom)
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

    There may be additional information required to represent variants to the shape, such as the radius of the
    rounded corners on a rounded rectangle, and these will be represented by subclassing this class to add
    shape specific behaviour.
    """

    def __init__(
            self,
            shape,
            top: float,
            left: float,
            width: float,
            height: float,
            format,
            text_vertical_alignment,
            text_flow,
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

        # ToDo: External text flag is only relevant for Visual Activities - should be optional
        self.external_text_flag = external_text_flag

        # These are constants used when rendering, but are set as object fields so can be changed if required.
        self.inside_text_margin = 5  # Probably interpreted as 5px
        self.outside_text_margin = 5  # Probably interpreted as 5px

    def get_text_x(self):
        """
        ToDo: Review whether get_text_x() should be defined in Plotable class or for each subclass.
        Text will be rendered and plotted separately from the shape to allow more flexibility in placing the text.
        So the plot dimensions for text will be calculated independently.

        Cases are:

        External Text Flag Not Set (For shapes other than milestones):
        - If text flow is left this means that the text will flow left out of the shape, starting from just inside
          the right edge of the shape
        - If text flow is right this means that the text will flow right out of the shape, starting from just inside the
          left edge of the shape

        External Text Flag Set. This will typically be for Milestones where the plotted shape is small (like a
        diamond) and the text will sit outside the shape.
        - If text flow is left this means that the text will flow left, starting just outside the left edge of the
          shape.
        - If text flow is right this means that the text will flow right, starting just outside the right edge of the
          shape.

        :return:
        """
        from plan_visual_django.models import VisualActivity
        if self.external_text_flag is True:
            if self.text_flow == VisualActivity.TextFlow.FLOW_TO_RIGHT:
                # Need to begin the plot outside the right edge of the shape
                text_x = self.get_right() + self.outside_text_margin
                text_align = "left"
            elif self.text_flow == VisualActivity.TextFlow.FLOW_TO_LEFT:
                text_x = self.left - self.outside_text_margin
                text_align = "right"
            elif self.text_flow == VisualActivity.TextFlow.FLOW_CENTRE:
                raise ValueError(f"Invalid text flow value for external text: {self.text_flow}")
            elif self.text_flow == VisualActivity.TextFlow.FLOW_CLIPPED:
                raise ValueError(f"Invalid text flow value for external text: {self.text_flow}")
            else:
                raise ValueError(f"Unrecognised text flow value for external text: {self.text_flow}")
        else:
            if (
                self.text_flow == VisualActivity.TextFlow.FLOW_TO_RIGHT or
                self.text_flow == VisualActivity.TextFlow.FLOW_CENTRE or
                self.text_flow == VisualActivity.TextFlow.FLOW_CLIPPED
            ):
                # Need to begin the plot outside the right edge of the shape
                text_x = self.left + self.outside_text_margin
                text_align = "left"
            elif self.text_flow == VisualActivity.TextFlow.FLOW_TO_LEFT:
                text_x = self.get_right() - self.outside_text_margin
                text_align = "right"
            elif self.text_flow == VisualActivity.TextFlow.FLOW_CENTRE:
                text_x = self.get_centre_x()
                text_align = "center"
            elif self.text_flow == VisualActivity.TextFlow.FLOW_CLIPPED:
                raise ValueError(f"Invalid text flow value for external text: {self.text_flow}")
            else:
                raise ValueError(f"Unrecognised text flow value for external text: {self.text_flow}")

        return text_x, text_align

    def get_text_y(self):
        from plan_visual_django.models import VisualActivity
        if self.text_vertical_alignment == VisualActivity.VerticalAlignment.TOP:
            text_y = self.top
            text_baseline = "top"
        elif self.text_vertical_alignment == VisualActivity.VerticalAlignment.MIDDLE:
            text_y = self.top + self.height / 2
            text_baseline = "middle"
        elif self.text_vertical_alignment == VisualActivity.VerticalAlignment.BOTTOM:
            text_y = self.get_bottom()
            text_baseline = "middle"
        else:
            raise ValueError(f"Unexpected value for text_vertical_alignment: {self.text_vertical_alignment}")

        return text_y, text_baseline

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

    def get_centre_x(self):
        return self.left + self.width / 2

    def get_centre_y(self):
        return self.top + self.height / 2

    def render(self, renderer):
        pass


def get_plotable(shape_name, **kwargs):
    """
    Decides which subclass of plotable is required based on which shape is to be plotted.

    :param shape:

    :return:
    """
    from plan_visual_django.models import PlotableShape
    plotable_factory_dispatch_table = {
        PlotableShape.PlotableShapeName.RECTANGLE: RectangleBasedPlotable,
        PlotableShape.PlotableShapeName.ROUNDED_RECTANGLE: RectangleBasedPlotable,
        PlotableShape.PlotableShapeName.DIAMOND: RectangleBasedPlotable,
        PlotableShape.PlotableShapeName.ISOSCELES_TRIANGLE: RectangleBasedPlotable
    }
    class_to_use = plotable_factory_dispatch_table[shape_name]
    return class_to_use(shape_name, **kwargs)
