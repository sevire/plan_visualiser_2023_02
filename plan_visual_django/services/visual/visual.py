from __future__ import annotations
from abc import ABC, abstractmethod
from plan_visual_django.models import VisualActivity, PlotableStyle, PlotableShapeType


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


class PlotableCollection():
    """
    A sequence of plotable elements or collections of plotable elements which define the structure of a visual. A given
    collection will subclass this class to allow collection specific behaviour to be defined.
    """
    def __init__(self):
        self.plotables: [Plotable | PlotableCollection] = []

    def get_dimensions(self):
        """
        Calculate the enclosing rectangle for this collection by getting all the rectangles for each plotable and
        working out the size of rectangle need to contain them all.
        :return:
        """
        rectangles = [plotable.get_dimensions() for plotable in self.plotables]
        min_left = min([left for top, left, width, height, right, bottom in rectangles])
        max_right = max([right for top, left, width, height, right, bottom in rectangles])
        min_top = min([top for top, left, width, height, right, bottom in rectangles])
        max_bottom = max([bottom for top, left, width, height, right, bottom in rectangles])
        height = max_bottom - min_top
        width = max_right - min_left

        left, top, width, height, right, bottom = min_left, min_top, width, height, max_right, max_bottom

        return left, top, width, height, right, bottom

    def add_plotable(self, plotable: Plotable | PlotableCollection):
        """
        Adds either a plotable object or a collection of plotable objects.

        Note order is important in that objects within a collection will be plotted in order, so
        if they overlap the later ones will sit on top of the earlier ones, unless the default layer
        is overridden within the plotable.

        :param plotable:
        :return:
        """
        self.plotables.append(plotable)


class Visual:
    """
    The top level class which represents a visual to be plotted in one of various media, including on a web page while
    configuring and laying out the visual.

    A visual comprises the following elements:

    - Settings: Visual level settings information, such as the width, height of the visual.
    - Plotable Collections: Collections of plotable objects typically related by function in the plot, such as timeline
      labels, swimlanes etc.
    - Plotable objects: Any object which can be drawn on an output medium.  It will have a size and shape and formatting
      information associated with it to allow it to be drawn.
    - Layers: At the time of writing I am not sure how to implement this but layers is a concept which will determine
      which objects sit on top of other objects. The principle is that Plotable Collections will sit within a layer
      and all Plotable objects within that collection will sit on the same layer, although it will be possible to
      override on an object by object basis.
    """
    def __init__(self):
        self.current_layer = 1
        self.visual = {}  # The visual will contain numbered layers of plotable components.

    def set_layer(self, layer_number: int):
        """
        Sets the layer within which future added objects will sit unless overridden.

        Layer is an integer starting from 1, but can be any number.  When plotting layers on the bottom
        layer are plotted first so that objects on higher numbered layers will sit on top of them.

        :param layer_number:
        :return:
        """
        self.current_layer = layer_number

    def increment_layer(self):
        self.current_layer += 1

    def add_collection(self, collection_name, collection: PlotableCollection=None):
        """
        Can add a passed in collection to the visual or create a new collection to be added to later.

        :param collection_name:
        :param collection:
        :return:
        """
        collection_to_store = PlotableCollection() if collection is None else collection
        self.visual[collection_name] = {
            "layer": self.current_layer,
            "plotables": collection_to_store
        }

    def add_plotable(self, collection_name, plotable: Plotable):
        if collection_name not in self.visual:
            raise ValueError(f"Attept to add plotable to non existent collection {collection_name}")
        else:
            self.visual[collection_name].append(plotable)

    def iter_collections(self):
        """
        Generator to iterate through all the collections in the visual in order of what layer they are in.

        Collections in the same layer will appear in the order they were added.
        :return:
        """
        ordered_layers = sorted(self.visual.items(), key=lambda x: x[1]['layer'])

        # ToDo: Tidy this up a bit - we seem to have layer information twice.
        for layer in ordered_layers:
            layer_name, layer_collection = layer
            collection = layer_collection['plotables']
            yield collection

    def get_dimensions(self):
        """
        Works out the width and height of the overall visual based on the dimensions and position of each collection
        of plotable items it contains.

        :return:
        """
        max_bottom = max([bottom for left, top, width, height, right, bottom in [collection.get_dimensions() for collection in self.iter_collections()]])
        max_right = max([right for left, top, width, height, right, bottom in [collection.get_dimensions() for collection in self.iter_collections()]])

        # As the min top and left will always be zero the max bottom and left are also height wnd width.
        # left, top, width, height, right, bottom
        return 0, 0, max_right, max_bottom, max_right, max_bottom


class PlotContext:
    """
    An object which will provide the relevant information to physically plot a visual, based on the medium in which it
    is to be plotted.  .

    Example use cases:

    1. Plotting on the Canvas element of a web page while laying out the visual, it will include the dimensions of the
       canvas element to allow objects to be scaled appropriately.
    2. Plotting into a PowerPoint slide, it would include a slide object to plot shapes onto and dimension information.
    """
    ...


class VisualRenderer(ABC):
    """
    An object which carries out the physical plotting of objects within the visual.
    """

    def plot_visual(self, visual: Visual):
        for collection in visual.iter_collections():
            self.plot_collection(collection)

    def plot_collection(self, collection: PlotableCollection):
        """
        Recursive method which iterates through a collection and either plots the object if it is a Plotable, or
        calls this method recursively if the item is another collection.

        :param collection:
        :return:
        """
        for item in collection.plotables:
            if type(item) == type(Plotable) or issubclass(type(item), Plotable):
                self.plot_plotable(item)
            elif type(item) == type(PlotableCollection):
                self.plot_collection(item)
            else:
                raise Exception(f"Unexpected type {type(item)} when plotting visual")

    @abstractmethod
    def plot_plotable(self, item: Plotable):
        pass
