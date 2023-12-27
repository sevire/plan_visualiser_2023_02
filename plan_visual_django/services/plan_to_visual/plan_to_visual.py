import datetime
from dataclasses import dataclass
from typing import Set

from plan_visual_django.models import VisualActivity, Color, PlotableStyle, Font, PlanVisual, TimelineForVisual, \
    PlotableShapeType
from plan_visual_django.services.general.date_utilities import first_day_of_month, last_day_of_month, \
    num_months_between_dates, DateIncrementUnit, increment_period, DatePlotter
from plan_visual_django.services.visual.renderers import CanvasRenderer, VisualRenderer
from plan_visual_django.services.visual.visual import Visual, PlotableCollection
from plan_visual_django.services.visual.visual_settings import VisualSettings, SwimlaneSettings


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
            self.swimlanes[swimlane.swim_lane_name] = {
                'swimlane_number': index + 1,
                'swimlane_name': swimlane.swim_lane_name,
                'swimlane_format': swimlane.plotable_style,
                'track_manager': TrackManager(visual_settings.track_height, visual_settings.track_gap)
            }


    def iter_swimlanes(self):
        ordered_swimlanes = sorted(self.swimlanes.values(), key=lambda x: x["swimlane_number"])
        for swimlane_record in ordered_swimlanes:
            yield swimlane_record['swimlane_number'], swimlane_record['swimlane_name'], swimlane_record['track_manager'], swimlane_record['swimlane_format']

    def add_activity_to_swimlane(self, activity):
        # Calculate position and height of activity based on selected vertical positioning type.
        v_positioning_type:VisualActivity.VerticalPositioningType = activity['vertical_positioning_type']
        track_number = 0  # Will be changed by logic below

        if v_positioning_type == VisualActivity.VerticalPositioningType.TRACK_NUMBER:
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
        for number, name, track_manager, format in self.iter_swimlanes():
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

    def create_collection(
            self,
            x_plot_start: float,
            x_plot_end: float,
            y_plot_start: float,
            y_plot_end: float
    ):
        """
        Creates a collection of plotables from what we know about the height of each swimlane
        :return:
        """
        collection = PlotableCollection()
        for number, name, track_manager, plotable_format in self.iter_swimlanes():
            # ToDo: Make shape for swimlane configurable at some point
            top = self.get_swimlane_top(name)

            # ToDo Remove hard coding of swimlane left at some point
            left = 0

            width = self.visual_settings.width
            height = track_manager.get_height_of_tracks()

            # swimlane_plotable = PlotableFactory.get_plotable(
            #     PlotableShapeType.PlotableShapeTypeName.RECTANGLE,
            #     top=top + y_plot_start,
            #     left=left + x_plot_start,
            #     width=width,
            #     height=height,
            #     format=plotable_format,
            #     text_vertical_alignment=VisualActivity.VerticalAlignment.TOP,
            #     text_flow=VisualActivity.TextFlow.FLOW_TO_RIGHT,
            #     text=name,
            #     external_text_flag=False
            # )

            # collection.add_plotable(swimlane_plotable)

        return collection


def timeline_configure_months(start_date: datetime.date, end_date: datetime.date):
    """
    Calculates information to drive timeline generator

    :param start_date:
    :param end_date:
    :return:
    """
    timeline_start_date = first_day_of_month(start_date)
    timeline_end_date = last_day_of_month(end_date)
    increment_units = DateIncrementUnit.MONTH
    increment_count = 1
    num_periods = num_months_between_dates(timeline_start_date, timeline_end_date)

    return timeline_start_date, timeline_end_date, increment_units, increment_count, num_periods


timeline_configure_dispatch_table = {
    TimelineForVisual.TimelineLabelType.MONTHS: timeline_configure_months
}
class TimelineLabelSet:
    """
    Object which represents the labels
    """
    def __init__(self, label_type: TimelineForVisual.TimelineLabelType):
        self.label_type = label_type


    def get_parameters_for_type(self, start_date:datetime.date, end_date:datetime.date, label_type: TimelineForVisual.TimelineLabelType):
        """
        Depending upon the type of labels required, the start date will vary as it will need to be aligned.  For
        example if it's quarters then start date will be the first of this month or an earlier month to align with
        the start of a quarter (where the first quarter of a year starts in Jan)

        :param label_type:
        :return:
        """
        timeline_dispatch_function = timeline_configure_dispatch_table[label_type]
        timeline_start_date, timeline_end_date, increment_units, increment_count, num_periods = timeline_dispatch_function(start_date, end_date)
        return timeline_start_date, timeline_end_date, increment_units, increment_count, num_periods

