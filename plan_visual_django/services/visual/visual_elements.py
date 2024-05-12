"""
For every object which is to be plotted within the visual, there will be a sub-class of VisualElement which represents
that object and on demand, will create the specific Plotable for that element.
"""
from datetime import date, datetime
from abc import ABC, abstractmethod
from plan_visual_django.services.general.date_utilities import month_increment, first_day_of_month, last_day_of_month, \
    num_months_between_dates, DatePlotter
from plan_visual_django.services.visual.plotables import Plotable, get_plotable
from plan_visual_django.services.visual.visual_settings import VisualSettings


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


class Timeline(VisualElementCollection):
    """
    Base class for any timeline.

    There is a bit of circular logic at play here.  A timeline can work out what it's start and end date would need
    to be based on the start and end dates of all the activities to be plotted.

    BUT: The different timelines will require different start and end dates as they need to align onto a specific
    unit, such as Quarter.

    Therefore, the dates which are passed in are the input dates, which the Timeline then uses to calculate and pass
    back the adjusted start and end dates for THIS timeline.  The caller will collect this information for all the
    different timelines and then set the visual start and end date which is what the Timeline will use to calculate
    it's actual Visual Elements.
    """
    def __init__(self, activity_start_date:datetime.date, activity_end_date:datetime.date, timeline_record):
        super().__init__()
        self.activity_start_date:date = activity_start_date
        self.activity_end_date:date = activity_end_date
        self.timeline_record = timeline_record

        self.visual_start_date:date|None = activity_start_date  # Will be set from outside orchestration logic.  Can't plot without.
        self.visual_end_date:date|None = activity_end_date  # Will be set from outside orchestration logic.  Can't plot without.

    @abstractmethod
    def calculate_date_range(self) -> (date, date):
        """
        Each timeline will need to calculate the start and end date for itself based on what type of timeline it is.

        :return: timeline_start_date, timeline_end_date
        """
        pass

    @classmethod
    def from_data_record(cls, start_date:date, end_date:date, timeline):
        """
        Works out which type of timeline to create based upon the type passed in the Timeline record from db, and
        then creates and returns that timeline.

        :param end_date:
        :param start_date:
        :param timeline:
        :return:
        """
        from plan_visual_django.models import TimelineForVisual
        if timeline.timeline_type == TimelineForVisual.TimelineLabelType.MONTHS:
            return MonthTimeline(start_date, end_date, timeline)
        elif timeline.timeline_type == TimelineForVisual.TimelineLabelType.QUARTERS:
            return QuarterTimeline(start_date, end_date, timeline)


class MonthTimeline(Timeline):
    def __init__(self, start_date: datetime.date, end_date: datetime.date, timeline_record):
        super().__init__(start_date, end_date, timeline_record)

    def create_collection(self, visual_settings, timeline_settings, top_offset=0, left_offset=0):
        """
        By the time this method is called, the calculate_date_range method will have been called to allow the
        orchestration logic to work out the range for the whole visual.

        :return:
        """
        x_plot_start = left_offset
        x_plot_end = visual_settings.width
        date_plotter = DatePlotter(self.visual_start_date, self.visual_end_date, x_plot_start, x_plot_end)

        num_periods = num_months_between_dates(self.visual_start_date, self.visual_end_date)
        for period_num in range(0, num_periods):
            period_start_date = month_increment(self.visual_start_date, period_num)
            period_end_date = last_day_of_month(period_start_date)

            # ToDo: Implement settings to specify format of month text
            text = period_start_date.strftime("%b")

            left = date_plotter.left(period_start_date)
            width = date_plotter.width(period_start_date, period_end_date)

            height = self.timeline_record.timeline_height

            # ToDo: Refactor vertical alignment and text flow so it isn't defined inside VisualActivity
            # ToDo: Replace hard-coded vertical alignment and text flow with config from database

            element = VisualElement()

            from plan_visual_django.models import PlotableShape
            element.shape=PlotableShape.PlotableShapeName.RECTANGLE
            element.top=top_offset
            element.left=left + left_offset
            element.width=width
            element.height=height
            element.plotable_style=self.timeline_record.plotable_style

            from plan_visual_django.models import VisualActivity
            element.text_vertical_alignment=VisualActivity.VerticalAlignment.MIDDLE
            element.text_flow=VisualActivity.TextFlow.FLOW_CENTRE

            element.text=text
            element.external_text_flag=False

            self.add_visual_element(element)

        return self

    def calculate_date_range(self):
        """
        Method wich will be called so that calling orchestration logic can work out the start and end date for the
        whole visual, based on the start, end date for each specific timeline, based on the timeline unit.

        The first and last date from the activities within the visual will be passed in.

        Example: For a month timeline we just need to calculate the first of the first month and the last day of
        the last month.

        :return:
        """
        timeline_start_date = first_day_of_month(self.activity_start_date)
        timeline_end_date = last_day_of_month(self.activity_end_date)

        return timeline_start_date, timeline_end_date


class QuarterTimeline(Timeline):
    def create_collection(self, visual_settings:VisualSettings, timeline_settings, top_offset=0, left_offset=0):
        x_plot_start = left_offset
        x_plot_end = visual_settings.width
        date_plotter = DatePlotter(self.visual_start_date, self.visual_end_date, x_plot_start, x_plot_end)

        num_periods = num_months_between_dates(self.visual_start_date, self.visual_end_date) // 3
        for period_num in range(0, num_periods):
            period_start_date = month_increment(self.visual_start_date, period_num * 3)
            period_end_date = last_day_of_month(month_increment(period_start_date, 3-1))

            # ToDo: Implement settings to specify format of month text
            text = f'{period_start_date.strftime("%b")} - {period_end_date.strftime("%b")}'

            left = date_plotter.left(period_start_date)
            width = date_plotter.width(period_start_date, period_end_date)

            height = self.timeline_record.timeline_height

            # ToDo: Refactor vertical alignment and text flow so it isn't defined inside VisualActivity
            # ToDo: Replace hard-coded vertical alignment and text flow with config from database

            element = VisualElement()

            from plan_visual_django.models import PlotableShape
            element.shape = PlotableShape.PlotableShapeName.RECTANGLE
            element.top = top_offset
            element.left = left + left_offset
            element.width = width
            element.height = height
            element.plotable_style = self.timeline_record.plotable_style
            from plan_visual_django.models import VisualActivity
            element.text_vertical_alignment = VisualActivity.VerticalAlignment.MIDDLE
            element.text_flow = VisualActivity.TextFlow.FLOW_CENTRE
            element.text = text
            element.external_text_flag = False

            self.add_visual_element(element)

        return self

    def __init__(self, start_date: datetime.date, end_date: datetime.date, timeline, month_offset=1):
        super().__init__(start_date, end_date, timeline)
        self.month_offset = month_offset

    def calculate_date_range(self):
        """
        For a quarter timeline we just need to calculate the start and end months and then the first and last day of
        those.  The month offset allows the caller to choose which months the quarters align to.

        :param offset:
        :return:
        """
        start_month = self.activity_start_date.month
        end_month = self.activity_end_date.month

        increment = (start_month - self.month_offset) % 3

        timeline_start_date_adjusted = month_increment(self.activity_start_date, -increment)
        timeline_start_date = first_day_of_month(timeline_start_date_adjusted)

        end_stage_1 = end_month - self.month_offset
        end_stage_2 = end_stage_1 % 3 - 2

        timeline_end_date_adjusted = month_increment(self.activity_end_date, -end_stage_2)
        timeline_end_date = last_day_of_month(timeline_end_date_adjusted)

        return timeline_start_date, timeline_end_date


class TimelineCollection(VisualElementCollection):
    """
    Collection of timelines each of which is a collection of timeline elements of different types.

    Example: A visual may require quarter labels and month labels.

    Depending upon which timelines are required, the start and end date for the whole visual will need to be adjusted
    so that the whole label fits on the visual.  So if quarters are included and the quarters are aligned to the start
    of the year (Jan) but the earliest activity is in March, then the start of the visual will be extended by two months.

    This class will manage the correct calculation of all the timelines within the visual.
    """

    def __init__(self, visual_start_date: date, visual_end_date:date, timelines: [], timeline_settings: dict):
        super().__init__()
        self.timeline_objects = None

        self.visual_start_date = visual_start_date
        self.visual_end_date = visual_end_date
        from plan_visual_django.models import TimelineForVisual
        self.timelines:[TimelineForVisual] = timelines
        self.timeline_settings = timeline_settings

        # The actual start and end date for the whole visual will be adjusted to ensure all the timelines fit.
        self.visual_start_date_final = visual_start_date
        self.visual_end_date_final = visual_end_date

    def initialise_collection(self):
        """
        Calculate the true start and end date for the visual based on the earliest and latest activity dates and
        the types of timeline we are adding.

        :return:
        """

        # Create dictionary of timeline objects based on timeline data from database
        self.timeline_objects = {timeline.timeline_name: Timeline.from_data_record(self.visual_start_date, self.visual_end_date, timeline) for timeline in self.timelines}

        # Now ask each timeline object to calculate its earliest and latest date and calculate the true start and end
        # date for the overall visual.
        self.visual_start_date_final = min([start_date for start_date, end_date in [timeline.calculate_date_range() for timeline in self.timeline_objects.values()]])
        self.visual_end_date_final = max([end_date for start_date, end_date in [timeline.calculate_date_range() for timeline in self.timeline_objects.values()]])

        # Now we know the start and end for the whole visual, set this for each timeline so they can calculate their
        # visual elements.

        for timeline_name, timeline_object in self.timeline_objects.items():
            timeline_object.visual_start_date = self.visual_start_date_final
            timeline_object.visual_end_date = self.visual_end_date_final

    def create_collection(self, visual_settings: VisualSettings, timeline_settings: any, top_offset=0, left_offset=0):
        for timeline_name, timeline_object in self.timeline_objects.items():
            timeline_collection = timeline_object.create_collection(visual_settings, timeline_settings, top_offset, left_offset)
            width, height = timeline_collection.get_dimensions()
            top_offset += height
            left_offset = 0
            self.add_collection(timeline_object)
        return self


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


class SwimlaneCollection(VisualElementCollection):
    """
    Collection which manages creation of swimlane visible elements.

    Swimlanes are a way of grouping activities together visually, to help the user understand the plan better.
    Activities within a swimlane are vertically aligned onto imaginary 'tracks' which are a set of horizontal bars of a
    specified height and with a specified gap between them.  A given activity is placed on a given track based on the
    layout options specified by the user when they create the visual.  Activities can take up more than one track to
    help certain activities to stand out.

    There will be a specified gap between each swimlane to help a clear distinction between lanes.  Swimlanes can be
    formatted in a number of different ways, including individually, or using alternating colours and other options
    (eventually).

    """
    def __init__(
            self,
            visual_start_date:date,
            visual_end_date:date,
            swimlane_records,
            activity_collection: ActivityCollection,
            visual_settings: VisualSettings,
            swimlane_settings
    ):
        """

        :param visual_start_date:
        :param visual_end_date:
        :param swimlane_records: From model: assumed to be in sequence chosen by user.
        :param visual_activity_records:
        :param visual_settings:
        :param swimlane_settings:
        """
        super().__init__()

        self.swimlane_settings = swimlane_settings
        self.visual_settings = visual_settings
        self.activity_collection = activity_collection
        self.swimlane_records = swimlane_records
        self.visual_end_date = visual_end_date
        self.visual_start_date = visual_start_date

    def create_collection(self, visual_settings: VisualSettings, collection_settings: any, top_offset=0, left_offset=0):
        """
        The swimlane_records passed in are from the database and include all swimlanes which were created for this
        visual.  So there shouldn't be any activities which include swimlanes which aren't in this list.  Additionally,
        the swimlane records should (must) be in the sequence selected by the user, and this is used in calculating the
        offset for the tracks in each swimlane.

        So we need to separate activities by swimlane, but maintain the order in the plan visual (which in turn will
        maintain the order from the plan), as that may be relevant for auto-layout algorithms.  It won't be relevant
        when the track is manually selected by the user.

        We are doing two things here:
        - Working out the vertical positioning for activities within a swimlane.
        - Calculating the swimlane heights once we know where the activities are placed.

        :param visual_settings:
        :param collection_settings:
        :return:
        """
        swimlane_top = top_offset
        first = True
        for index, swimlane in enumerate(self.swimlane_records):
            swimlane_name = swimlane.swim_lane_name
            activities_for_swimlane = [activity for activity in self.activity_collection.visual_activity_records if activity["swimlane"] == swimlane_name]
            if len(activities_for_swimlane) > 0:
                max_track_for_swimlane = 0

                # If this isn't the first swimlane, add margin.
                if first is True:
                    first = False
                else:
                    swimlane_top += self.visual_settings.swimlane_gap

                for activity in activities_for_swimlane:
                    # We need to go through the activities for a swimlane sequentially because there will be layout options
                    # Where the vertical position of the current activity is directly related to that of the previous one.
                    from plan_visual_django.models import VisualActivity
                    v_positioning_type: VisualActivity.VerticalPositioningType = activity['vertical_positioning_type']
                    if v_positioning_type == VisualActivity.VerticalPositioningType.TRACK_NUMBER:
                        track_number_start = activity['vertical_positioning_value']
                        num_tracks = activity['height_in_tracks']
                        track_number_end = track_number_start + num_tracks - 1
                    else:
                        raise ValueError(f"Positioning type {v_positioning_type} not yet implemented")
                    max_track_for_swimlane = max(max_track_for_swimlane, track_number_end)

                    # ToDo: Remove this hack for the track gap and make the code work properly!
                    if track_number_start > 1:
                        gap_if_required = visual_settings.track_gap
                    else:
                        gap_if_required = 0

                    activity_top = swimlane_top + self.calculate_height_of_tracks(track_number_start-1) + gap_if_required

                    height = self.calculate_height_of_tracks(num_tracks)
                    self.activity_collection.set_activity_vertical_plot_attributes(activity['unique_id_from_plan'], activity_top, height)

                from plan_visual_django.models import PlotableShape, VisualActivity
                shape = PlotableShape.PlotableShapeName.RECTANGLE
                plotable_style = swimlane.plotable_style

                text_vertical_alignment = VisualActivity.VerticalAlignment.TOP
                text_flow = VisualActivity.TextFlow.FLOW_TO_RIGHT
                text = swimlane_name
                width = self.visual_settings.width
                swimlane_height = self.calculate_height_of_tracks(max_track_for_swimlane)

                element = VisualElement()

                element.shape = shape
                element.top = swimlane_top
                element.left = left_offset
                element.width = width
                element.height = swimlane_height
                element.plotable_style = plotable_style
                element.text_vertical_alignment = text_vertical_alignment
                element.text_flow = text_flow
                element.text = text
                element.external_text_flag = False

                self.add_visual_element(element)

                swimlane_top += swimlane_height


        return self

    def calculate_height_of_tracks(self, max_track_num):
        """
        Calculates the height of a sequence of tracks within a swimlane - doesn't include any margins.
        :return:
        """
        if max_track_num == 0:
            return 0
        else:
            track_height = self.visual_settings.track_height
            height = max_track_num * track_height + (max_track_num - 1) * self.visual_settings.track_gap

            return height
