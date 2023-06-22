import datetime
from dataclasses import dataclass
from typing import Iterable, Tuple, Set

from plan_visual_django.services.drawing.plan_visual_plotter_types import ShapeType
from plan_visual_django.services.visual.formatting import VerticalPositioningOption, PlotableFormat, LineFormat, \
    FillFormat, PlotableColor, TextVerticalAlign, TextFlow
from plan_visual_django.services.visual.visual import Visual, Plotable, VisualPlotter, PlotableFactory, \
    PlotableCollection
from plan_visual_django.services.visual.visual_settings import VisualSettings, SwimlaneSettings


class DatePlotter:
    """
    Utility class which helps with calculating the x-coordinate for a visual.
    """
    def __init__(self, earliest_date: datetime.date, latest_date: datetime.date, x_plot_start: float, x_plot_end: float):
        """
        Sets up by working out the number of days the activities cover based on the supplied list of start and end
        dates.

        Then for a given date it calculates the x value to use when plotting on the visual.

        """
        self.latest_date = latest_date
        self.earliest_date = earliest_date
        self.num_days_in_visual = self.num_days_between_dates(earliest_date, latest_date)
        self.x_plot_start = x_plot_start
        self.x_plot_end = x_plot_end

    @property
    def activity_plot_width(self):
        return self.x_plot_end - self.x_plot_start

    @staticmethod
    def get_earliest_latest_dates(activities:[]):
        """
        Get earliest start date and latest end date from list of tuples of start and end date

        :param activities:
        :return:
        """
        earliest_date = min([start_date for start_date, _ in activities])
        latest_date = max([end_date for _, end_date in activities])

        return earliest_date, latest_date


    @staticmethod
    def num_days_between_dates(start_date, end_date):
        num_days = end_date - start_date + datetime.timedelta(days=1)

        return num_days

    def x_coordinate_for_date(self, date: datetime.date, end_flag = False, mid_point=False) -> float:
        """
        Calculates the x coordinate for a given date within the visual.

        Note that as a date isn't a point but an interval, and the x coordinate can be used to represent either
        the start of the day (start_date) or the end of the day (end_date) the end_flag is used to indicate
        which case is required.

        :param date:
        :param end_flag:
        :return:
        """

        additional_amount = datetime.timedelta(days=0)
        if end_flag:
            additional_amount = datetime.timedelta(days=1)
        elif mid_point:
            additional_amount = datetime.timedelta(hours=12)

        day_number_in_activities = date - self.earliest_date + additional_amount
        proportion_of_width = day_number_in_activities / self.num_days_in_visual
        x = self.x_plot_start + proportion_of_width * self.activity_plot_width

        return x

    def left(self, date: datetime.date):
        return self.x_coordinate_for_date(date)

    def width(self, start_date: datetime.date, end_date: datetime.date):
        width = self.x_coordinate_for_date(end_date, end_flag=True) - self.left(start_date)

        return width

    def midpoint(self, date):
        """
        Used mostly for plotting milestones (probably) - calculates the mid-point of a given day.

        :param date:
        :return:
        """
        midpoint = self.x_coordinate_for_date(date, mid_point=True)
        return midpoint


class ActivityManager:
    """
    Utility class which helps to create the activity plotables to add to the visual.
    """
    def __init__(
            self,
            activities: [],
            x_plot_start: float,
            x_plot_end: float,
            y_plot_start: float,
            y_plot_end: float,
            visual_settings: VisualSettings
    ):
        self.x_start = x_plot_start
        self.y_start = y_plot_start
        self.x_end = x_plot_end
        self.y_end = y_plot_end
        self.visual_settings = visual_settings

        self.swimlane_manager = SwimlaneManager(visual_settings)

        self.activity_collection: PlotableCollection = PlotableCollection()
        self.activities = activities
        dates = [(activity['start_date'], activity['end_date']) for activity in self.activities]
        earliest, latest = DatePlotter.get_earliest_latest_dates(dates)
        self.date_plotter = DatePlotter(earliest, latest, x_plot_start, x_plot_end)

    def calculate_vertical_position(self, activity, track_number: int):
        """
        Calculates where an activity should sit vertically within a swimlane based on the layout information provided
        by the user.

        NOTE: This is a very simple initial implementation which doesn't allow for sophisticated layout options.

        ToDo: Come back and add other use cases (swimlanes, relative positioning etc)

        :param track_number:
        :param activity:
        :return:
        """
        top = self.swimlane_manager.get_track_top_within_swimlane(activity['swimlane'], track_number)
        height = self.swimlane_manager.get_plotable_height(
            swimlane_name=activity['swimlane'],
            num_tracks=activity['height_in_tracks'])

        return top, height

    def create_activity_collection(self):
        """
        Turn activities with dates into plotable objects with precise coordinates.

        Also involves creation of swimlanes and laying out of objects on tracks.  Note that the track number isn't
        always specified by the user as layout options include (or will include) options to position relative to
        the previous activity or just to auto calculate the layout.
        :return:
        """

        # Parse activities twice - first time to calculate swimlanes and tracks, then to calculate plotables

        # First calculate swimlanes and add track_number for each activity so that we can calculate vertical position
        # of each activity correctly when we add them to the visual.
        activities_plus_tracks = []
        for activity in self.activities:
            # The returned track number will be either that specified by user or calculated by logic of preferred layout
            # option selected.
            track_number = self.swimlane_manager.add_activity_to_swimlane(activity)
            activities_plus_tracks.append({
                'track_number': track_number,
                'activity': activity
            })

        # Second parse calculates the shape, dimensions and position for each activity in the visual.
        for activity_record in activities_plus_tracks:
            activity = activity_record["activity"]
            track_number = activity_record["track_number"]
            top, height = self.calculate_vertical_position(activity, track_number)
            if activity['duration'] == 0:
                # This is a milestone so we plot in the middle of the day to the specified width for a milestone.
                left = self.date_plotter.midpoint(activity['start_date']) - self.visual_settings.milestone_width/2
                width = self.visual_settings.milestone_width
            else:
                left = self.date_plotter.left(activity['start_date'])
                width = self.date_plotter.width(activity['start_date'], activity['end_date'])
            shape = ShapeType[activity['plotable_shape']]
            plotable_format = PlotableFormat.from_db_choice(activity['plotable_style'])

            text_vertical_alignment = TextVerticalAlign(activity['text_vertical_alignment'])
            text_flow = TextFlow(activity['text_flow'])
            text = activity['activity_name']

            plotable = PlotableFactory.get_plotable(
                shape,
                top=top,
                left=left,
                width=width,
                height=height,
                format=plotable_format,
                text_vertical_alignment=text_vertical_alignment,
                text_flow=text_flow,
                text=text
            )
            self.activity_collection.add_plotable(plotable)

        return self.activity_collection, self.swimlane_manager

@dataclass
class TrackManager:
    """
    Manages information and calculations about the tracks which are used to position activities on the visual.

    Each activity will be aligned to a track within a swimlane, and will span one or more tracks.  There will be a gap
    between tracks.
    """
    track_height: float
    track_gap: float


    def __post_init__(self):
        """
        Not all tracks will contain activities so allow for gaps - that's why it's not a list.
        We just need to keep a record of which tracks have been added as this will drive the height of the swimlane,
        for example.  So a set is used.

        Don't add any tracks until added by user as if there end up not being any tracks in a swimlane we may not
        plot the swimlane (not our decision to make!).

        :return:
        """
        self.tracks: Set[int] = set()
        self.current_track = None  # Used for layout options where activities are laid out relative to previous ones.

    def add_tracks_for_activity(self, track_number: int, num_tracks: int):
        """
        Will be called while iterating through activities.  If tracks already exist to accommodate the activity then
        nothing needs to be done.  Otherwise add new tracks as required.

        :param num_tracks:
        :param track_number:
        :return:
        """
        for track_to_add in range(0, int(num_tracks)):
            track_num = track_number + track_to_add
            self._add_track(track_num)

    def _add_track(self, track_num: int = None):
        """
        Add supplied track number if not already existing.  If it's None then add the next track and return it's number.
        If it's not None then just return the track number back.
        :param track_num:
        :return:
        """
        if track_num is None:
            track_num_to_add = max(self.tracks) + 1
        else:
            track_num_to_add = track_num

        self.tracks.add(track_num_to_add)
        self.current_track = track_num_to_add

        return track_num_to_add

    def get_num_tracks(self):
        """
        Note there may be gaps in the set of track numbers but tracks will be plotted as a sequence.  Gaps just mean
        that no activities have been plotted in the missing track, not that the track won't take space up in the visual

        :return:
        """
        return max(self.tracks)

    def get_num_occupied_tracks(self):
        return len(self.tracks)


    def get_num_unoccupied_tracks(self):
        return self.get_num_tracks() - self.get_num_occupied_tracks()


    def get_height_of_tracks(self, num_tracks = None):
        """
        The height of a collection of tracks isn't dependent upon the individual tracks, just the track height and gap.

        :param num_tracks:
        :return:
        """
        if num_tracks is None: num_tracks = self.get_num_tracks()
        height = num_tracks * self.track_height + (num_tracks - 1) * self.track_gap

        return height

    def get_relative_track_top(self, track_num: int):
        height_of_tracks_before_this = (track_num - 1) * (self.track_height + self.track_gap)
        relative_track_top = height_of_tracks_before_this  # Should I be adding some sort of fudge factor here?

        return relative_track_top


class SwimlaneManager:
    """
    Manages creation of swimlanes as activities are processed into the visual, and also drives some vertical
    positioning calculations which are swimlane dependent (e.g. vertical position (top)).
    """
    def __init__(self, visual_settings: VisualSettings):
        self.visual_settings = visual_settings
        self.swimlanes = {}

        # Initialise swimlane structure to reflect the order of swimlanes specified in settings.
        for index, swimlane in enumerate(visual_settings.swimlane_settings.swimlanes):
            self.swimlanes[swimlane] = {
                'swimlane_number': index + 1,
                'swimlane_name': swimlane,
                'track_manager': TrackManager(visual_settings.track_height, visual_settings.track_gap)
            }


    def iter_swimlanes(self):
        ordered_swimlanes = sorted(self.swimlanes.values(), key=lambda x: x["swimlane_number"])
        for swimlane_record in ordered_swimlanes:
            yield swimlane_record['swimlane_number'], swimlane_record['swimlane_name'], swimlane_record['track_manager']

    def add_activity_to_swimlane(self, activity):
        # Calculate position and height of activity based on selected vertical positioning type.
        v_positioning_type:VerticalPositioningOption = activity['vertical_positioning_type']
        track_number = 0  # Will be changed by logic below

        if v_positioning_type == VerticalPositioningOption.TRACK_NUMBER:
            track_number = activity['vertical_positioning_value']
            num_tracks = activity['height_in_tracks']
            swimlane_to_add = activity['swimlane']
            self.swimlanes[swimlane_to_add]['track_manager'].add_tracks_for_activity(track_number, num_tracks)
            # ToDo: Add other vertical positioning options
        else:
            raise ValueError(f"Positioning type {v_positioning_type} not yet implemented")

        return track_number

    def get_swimlane_height(self, swimlane_name):
        """
        Calculates the height of a swimlane, from top of first track to bottom of last track (no margins included)

        :param swimlane_name:
        :return:
        """
        return self.swimlanes[swimlane_name]['track_manager'].get_height_of_tracks()

    def get_swimlane_top(self, swimlane_name):
        """
        Returns the relative top of a swimlane based on the height of preceding swimlanes and the gaps between
        swimlanes.

        :param swimlane_name:
        :return:
        """
        # First get swimlane information into swimlane number order.
        ordered_swimlanes = sorted(self.swimlanes.values(), key=lambda x: x["swimlane_number"])

        # Now iterate through the swimlanes adding to the total height until we get to the one we are looking at.
        height = 0
        for number, name, track_manager in self.iter_swimlanes():
            # Only process up to the named swimlane.
            if name == swimlane_name:
                break
            swimlane_height = track_manager.get_height_of_tracks()
            swimlane_gap = self.visual_settings.swimlane_settings.swimlane_gap
            height += swimlane_height + swimlane_gap

        top = height  # Not sure whether I should be adding a tiny additional amount here
        # ToDo: Think about how to adjust plot value between end of one object and the start of the next.

        return top

    def get_track_top_within_swimlane(self, swimlane_name: str, track_num: int):
        """
        for a track within a swimlane, works out the position of the top of the track within the set of all swimlanes.

        NOTE:

        - Doesn't take account of how the swimlanes are positioned within the overall visual (it doesn't know).
        - Takes account of gap between swimlane
        - Only valid if track number is one which actually exists within the specified swimlane

        :param swimlane_name:
        :param track_num: Track number within supplied swimlane.
        :return:
        """

        num_tracks = self.swimlanes[swimlane_name]['track_manager'].get_num_tracks()
        if track_num > num_tracks:
            raise ValueError(f"Track number {track_num}, for swimlane {swimlane_name}, invalid, only {num_tracks} available")
        swimlane_top = self.get_swimlane_top(swimlane_name)
        relative_track_top = self.swimlanes[swimlane_name]['track_manager'].get_relative_track_top(track_num)

        track_top_within_swimlane = swimlane_top + relative_track_top

        return track_top_within_swimlane

    def get_plotable_height(self, swimlane_name: str, num_tracks: int):
        return self.swimlanes[swimlane_name]["track_manager"].get_height_of_tracks(num_tracks)

    def create_collection(self):
        """
        Creates a collection of plotables from what we know about the height of each swimlane
        :return:
        """
        collection = PlotableCollection()
        for number, name, track_manager in self.iter_swimlanes():
            # ToDo: Make shape for swimlane configurable at some point
            top = self.get_swimlane_top(name)

            # ToDo Remove hard coding of swimlane left at some point
            left = 0

            width = self.visual_settings.width
            height = track_manager.get_height_of_tracks()

            line_format = LineFormat(PlotableColor(255, 150, 150), 1)
            fill_format = FillFormat(PlotableColor(150, 255, 150))
            plotable_format = PlotableFormat(line_format, fill_format)

            swimlane_plotable = PlotableFactory.get_plotable(
                ShapeType.RECTANGLE,
                top=top,
                left=left,
                width=width,
                height=height,
                format=plotable_format,
                text_vertical_alignment = TextVerticalAlign.TOP,
                text_flow = TextFlow.FLOW_TO_RIGHT,
                text = name
            )

            collection.add_plotable(swimlane_plotable)

        return collection


class VisualManager:
    """
    Takes plan data from the model (Database) and transforms it into the object representation of a visual (Visual)
    which can then be plotted onto a given medium (including Canvas).

    Specifically:
    - Works out the date span of the plan to be plotted to drive conversion to plot data.
    - Works out the vertical position and height of each activity based on layout inforation provided by user.
    - Adds plotable collections as required for:
      - Title  ToDo: Add Title plotable collection
      - Timeline Labels ToDo: Add Timeline label plotable collection
      - Swimlanes ToDo: Add Swimlane plotable collection

    Specifically converts date information to associated x coordinates/width for plotting, and layout information to y
    coordinates/heights etc.
    """
    def __init__(
            self,
            visual_activity_data,
            visual_settings: VisualSettings
    ):
        """
        The visual is generated from the information provided to the object.  The minimum required information to
        create a visual is the visual activity data which contains all the activities to plot, and the visual settings
        object which provides important information such as the size of the visual in the units it will be plotted in.

        :param visual_activity_data: A list of all the activities with both plan related information and layout related
        information.
        :param visual_settings: Key information required to plot the visual, such as the size of the visual, required
        to convert the dates into actual coordinates for plotting.
        """
        self.visual = Visual()
        self.visual_activity_data = visual_activity_data
        self.visual_settings = visual_settings
        self.swimlane_manager = None  # Will be created when creating activity collection of plotables.

    def add_activities_to_visual(
            self,
            x_plot_start: float,
            x_plot_end: float,
            y_plot_start: float,
            y_plot_end: float
    ):
        # ToDo: Management of which layer each component goes into needs to be managed somewhere not hard coded
        # ToDo: Stop hard-coding the layer which activities go into
        self.visual.set_layer(2)  # Activities need to be on top of the swimlanes.
        activity_manager = ActivityManager(
            self.visual_activity_data,
            x_plot_start,
            x_plot_end,
            y_plot_start,
            y_plot_end,
            self.visual_settings
        )
        collection, self.swimlane_manager = activity_manager.create_activity_collection()
        self.visual.add_collection(collection_name="activities", collection=collection)

    def add_swimlanes_to_visual(self, width):
        # ToDo: Stop hard-coding the layer which swimlanes go into
        self.visual.set_layer(1)
        swimlane_collection = self.swimlane_manager.create_collection()
        self.visual.add_collection(collection_name="swimlanes", collection=swimlane_collection)

    def extract_visual_properties(self):
        """
        Calculates/derives key properties of the plan
        :return:
        """
        pass

    def plot_visual(self, plotter: VisualPlotter):
        ret = plotter.plot_visual(self.visual)

        return ret
