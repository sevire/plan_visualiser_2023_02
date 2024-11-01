"""
For every object which is to be plotted within the visual, there will be a sub-class of VisualElement which represents
that object and on demand, will create the specific Plotable for that element.
"""
from datetime import date
from abc import ABC
from plan_visual_django.services.general.date_utilities import DatePlotter
from plan_visual_django.services.visual.rendering.plotables import Plotable, get_plotable
from plan_visual_django.services.visual.model.visual_settings import VisualSettings


class VisualElement:
    """
    Base class for all visual elements.

    Typically, a visual element will calculate certain properties to be plotted based on its own attributes, and others
    from values passed in at the time of plotting, which will depend upon other elements on the visual which a given
    element has no knowledge of.

    So the base class will define a method which allows the caller to set up plotable attributes which are common, and
    then when the plot_element method is called, it will assume that all values have been set.
    """
    def __init__(self):
        """
        Set up initial values for all attributes which are common to most plotables.  Then the child class can set up
        the actual values for those attributes and if there aren't any non-standard ones then the base version of
        plot_element will work, otherwise it will need to be sub-classed.
        """
        self.plotable_id = "(undefined)"
        self.shape = None
        self.top = None
        self.left = None
        self.width = None
        self.height = None
        self.plotable_style = None
        self.text_vertical_alignment = None
        self.text_flow = None
        self.text = None
        self.external_text_flag = None

    def plot_element(self):
        plotable:Plotable = get_plotable(
            plotable_id=self.plotable_id,
            shape_name=self.shape,
            top=self.top,
            left=self.left,
            width=self.width,
            height=self.height,
            format=self.plotable_style,
            text_vertical_alignment=self.text_vertical_alignment,
            text_flow=self.text_flow,
            text=self.text,
            external_text_flag=self.external_text_flag
        )
        return plotable

    def render_element(self, renderer):
        plotable = self.plot_element()
        renderer.plot_plotable(plotable)

    def _set_element_specific_attributes(self, **kwargs):
        """
        This is a base level method but when called, the attributes which are set will depend upon the element type.
        :return:
        """
        for name, value in kwargs.items():
            setattr(self, name, value)

    def calculate_attributes(self):
        """
        Calculate the plotable attributes for this element which are specific to the attributes of the element, rather
        than passed in as an attribute from outside.

        :return:
        """
        pass

    def __str__(self):
        return f"{self.shape}, {self.text}, (top: {self.top:.2f}, left: {self.left:.2f}, width: {self.width:.2f}, height: {self.height:.2f})"


class VisualElementCollection(ABC):
    """
    Base class for any collection of visual elements which need to be treated as a cohesive set.

    Examples are Activities, Swimlanes, Timeline Labels and Timeline, which is a collection of Timeline Labels
    """
    def __init__(self):
        self._collection:[VisualElement|"VisualElementCollection"] = []

    @property
    def collection(self):
        """
        If a given collection sub-class uses a different structure (e.g. Activities which need a unique id) then this
        will convert to a list like object for use in methods which require that.
        :return:
        """
        return self._collection

    def add_visual_element(self, visual_element:VisualElement, **kwargs):
        self._collection.append(visual_element)

    def initialise_collection(self):
        """
        Subclass specific method which carries out one-off activities which prepare for the creation of each item
        within the collection.

        :return:
        """
        pass

    def create_collection(self, visual_settings:VisualSettings, collection_settings: any, top_offset=0, left_offset=0):
        """
        Subclass specific method which creates a plotable for each element of this collection and adds it to the
        collection.

        :return:
        """
        pass

    def add_collection(self, visual_element_collection:"VisualElementCollection"):
        self._collection.append(visual_element_collection)

    def iter(self, level:int=0, include_collections: bool=False):
        """
        Recursively traverses this collection and any sub-collections, essentially flattening the structure into a
        list of VisualElements, in the right order to plot.

        Optionally includes the collections in the yielded output, mostly to support debug printing of a collection.
        :return:
        """
        for element in self.collection:
            if isinstance(element, VisualElementCollection) or issubclass(type(element), VisualElementCollection):
                # This element is another collection so - return if flag set
                if include_collections is True:
                    yield element, level

                # Now recursively call
                yield from element.iter(level+1, include_collections=include_collections)
            else:
                yield element, level

    def get_dimensions(self):
        """
        Returns dimensions of this collection by looking at the dimensions and position of individual elements.

        :return:
        """
        min_left = 0
        max_right = -1
        min_top = 0
        max_bottom = -1

        for element, level in self.iter():
            min_left = min(min_left, element.left)

            element_right = element.left + element.width
            max_right = element_right if max_right == -1 else max(max_right, element_right)

            min_top = min(min_top, element.top)
            element_bottom = element.top + element.height
            max_bottom = element_bottom if max_bottom == -1 else max(max_bottom, element_bottom)

        width = max_right - min_left
        height = max_bottom - min_top

        return width, height

    def print_collection(self):
        """
        Lists all the elements of all the collections in a useful way to help in debugging etc.
        :return:
        """
        print(f"Printing collection...")
        for element, level in self.iter(include_collections=True):
            indent_string = "   " * level
            if isinstance(element, VisualElementCollection) or issubclass(type(element), VisualElementCollection):
                print(indent_string + f"Collection of Type {type(element).__name__}...")
            else:
                print(indent_string + str(element))


class ActivityCollection(VisualElementCollection):
    def __init__(
            self,
            visual_start_date: date,
            visual_end_date: date,
            visual_activity_records,
            visual_settings,
            x_start: float,
            x_end: float,
            y_start: float,
            y_end: float,

    ):
        super().__init__()
        self.x_start = x_start
        self.x_end = x_end
        self.y_start = y_start
        self.y_end = y_end
        self.visual_start_date = visual_start_date
        self.visual_end_date = visual_end_date
        self.visual_activity_records = visual_activity_records
        self.visual_settings = visual_settings

        self.date_plotter = DatePlotter(self.visual_start_date, self.visual_end_date, self.x_start, self.x_end)

        # We need to maintain the order of activities that are passed in but also need to access them by unique id
        # to allow the vertical positioning to be set from the swimlane manager.
        # NOTE: This relies on the dict being ordered, which is true for modern versions of Python.
        self._collection: {str: (Plotable|None)} = {}

    @property
    def collection(self):
        return list(self._collection.values())

    def add_visual_element(self, visual_element, unique_id=None):
        """
        Overriding because the collection is stored in a dict not a list.

        :param unique_id:
        :param visual_element:
        :return:
        """
        self._collection[unique_id] = visual_element

    def set_activity_vertical_plot_attributes(self, unique_id: str, top: float, height: float):
        """
        Typically called from the swimlane collection class and will set the vertical height for each activity as it is
        parsed to calculated the swimlane height.

        :return:
        """
        visual_element_for_this_activity = self._collection[unique_id]
        if visual_element_for_this_activity is None:
            raise ValueError(f"Plotable for {unique_id} not initialised - can't set top")
        visual_element_for_this_activity.top = top
        visual_element_for_this_activity.height = height

    def initialise_collection(self):
        pass

    def create_collection(self, visual_settings: VisualSettings, collection_settings: any, top_offset=0, left_offset=0):
        for activity in self.visual_activity_records:
            # Note and height will be calculated by SwimlaneCollection.
            if activity['milestone_flag'] is True:
                # This is a milestone so we plot in the middle of the day to the specified width for a milestone.
                left = self.date_plotter.midpoint(activity['start_date']) - self.visual_settings.milestone_width / 2
                width = self.visual_settings.milestone_width

                # The text for milestones is plotted outside the shape as typically it's a small constant width shape
                # like a diamond or triangle.
                external_text_flag = True
            else:
                left = self.date_plotter.left(activity['start_date'])
                width = self.date_plotter.width(activity['start_date'], activity['end_date'])
                external_text_flag = False

            shape = activity['plotable_shape']
            plotable_style = activity['plotable_style']

            from plan_visual_django.models import VisualActivity
            text_vertical_alignment = VisualActivity.VerticalAlignment(activity['text_vertical_alignment'])
            text_flow = VisualActivity.TextFlow(activity['text_flow'])
            text = activity['activity_name']

            # When we create the plotable, add in the x, y offset passed in.

            element = VisualElement()

            element.shape=shape
            element.top=None
            element.left=left
            element.width=width
            element.height=None
            element.plotable_style=plotable_style
            element.text_vertical_alignment=text_vertical_alignment
            element.text_flow=text_flow
            element.text=text
            element.external_text_flag=external_text_flag

            self.add_visual_element(element, unique_id=activity["unique_id_from_plan"])

        return self

