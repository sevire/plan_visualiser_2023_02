"""
Includes algorithms for automatic layout of the plan.

The main algorithm is the following:
1. All milestones in a single swimlane laid out chronologically.
2. Creating swimlanes and activities by using the structure of the plan. (that is Level information).
"""
import logging
from typing import List

from plan_visual_django.services.plan_file_utilities.plan_tree import PlanTree
from plan_visual_django.services.service_utilities.service_response import ServiceResponse
from django.db import IntegrityError
from django.db.models import Subquery, OuterRef
from plan_visual_django.exceptions import DuplicateSwimlaneException
from plan_visual_django.models import SwimlaneForVisual, VisualActivity, PlanVisual, PlanActivity, \
    DEFAULT_HEIGHT_IN_TRACKS, DEFAULT_TEXT_HORIZONTAL_ALIGNMENT, DEFAULT_TEXT_VERTICAL_ALIGNMENT, DEFAULT_TEXT_FLOW, \
    Plan
from plan_visual_django.services.general.date_utilities import proportion_between_dates
from plan_visual_django.services.service_utilities.service_response import ServiceStatusCode
from plan_visual_django.services.visual.model.full_autolayout_algorithm import build_initial_layout, LayoutOptions
from plan_visual_django.services.visual.model.visual_settings import VisualSettings
from django.db import transaction

logger = logging.getLogger(__name__)

class VisualLayoutManager:
    """
    Class which provides utilities for adding, moving or removing activities from a visual according to various
    different schemes, such as to add activities or a given level, to add sub-activities for an activity etc.
    """
    def __init__(self, visual_id_for_plan):
        self.visual_for_plan = PlanVisual.objects.get(id=visual_id_for_plan)
        self.plan = self.visual_for_plan.plan
        self.plan_activities = self.plan.planactivity_set.all()  # Note this creates a queryset which may be modified.
        self.visual_settings: VisualSettings = VisualSettings(visual_id_for_plan)
        self.plan_tree: PlanTree = self.plan.get_plan_tree()

    def create_milestone_swimlane(
        self,
        swimlane_plotable_style,
        milestone_plotable_style,
        milestone_plotable_shape
    ):
        """
        Creates a new swimlane which includes all the milestones from the plan, and sorts them chronologically.

        Works by:
        1. Get all the milestones from the plan in date order.
        2. Create a new swimlane for the milestones.
        3. For each milestone, check whether it is already in the visual, and if it is, move it to the new swimlane.
           If not then add a new visual activity and place within the milestone swimlane.

        :return:
        """
        # Create swimlane for all Milestones.  If there already is one we can't proceed as we don't know what's in it.
        try:
            swimlane = SwimlaneForVisual.objects.create(
                plan_visual=self.visual_for_plan,
                swim_lane_name="Milestones",
                plotable_style=swimlane_plotable_style,
                sequence_number=500
            )
        except IntegrityError as e:
            raise DuplicateSwimlaneException("Swimlane already exists for milestones") from e

        milestone_plan_activities = self.plan_activities.filter(milestone_flag=True).order_by('start_date')

        # Only proceed if there is at least one milestone

        if len(milestone_plan_activities) == 0:
            print("No milestones in plan, so can't create swimlane")
            return
        earliest_milestone_date = milestone_plan_activities.first().start_date
        latest_milestone_date = milestone_plan_activities.last().start_date
        mid_point_date = proportion_between_dates(earliest_milestone_date, latest_milestone_date, 0.5)

        for index, plan_activity_for_milestone in enumerate(milestone_plan_activities):
            # For now just have one milestone per track and add them in date order.
            track_number = index + 2  # Start at 2 as 1 is the swimlane header

            # Set some attributes which we will need later
            unique_id_from_plan = plan_activity_for_milestone.unique_sticky_activity_id
            if plan_activity_for_milestone.start_date < mid_point_date:
                text_flow = VisualActivity.TextFlow.FLOW_TO_RIGHT
            else:
                text_flow = VisualActivity.TextFlow.FLOW_TO_LEFT

            # Check whether this activity from the plan is already in the visual
            try:
                plan_activity_for_milestone = VisualActivity.objects.get(
                    visual=self.visual_for_plan, unique_id_from_plan=unique_id_from_plan
                )
            except VisualActivity.DoesNotExist:
                # This milestone is not already in the visual so add it.

                VisualActivity.objects.create(
                    visual=self.visual_for_plan,
                    swimlane=swimlane,
                    unique_id_from_plan=unique_id_from_plan,
                    enabled=True,
                    plotable_shape=milestone_plotable_shape,
                    vertical_positioning_value=track_number,
                    height_in_tracks=1,
                    text_horizontal_alignment=VisualActivity.HorizontalAlignment.CENTER,
                    text_vertical_alignment=VisualActivity.VerticalAlignment.MIDDLE,
                    text_flow=text_flow,
                    plotable_style=milestone_plotable_style,
                )
            else:
                # The milestone has been added but may have subsequently been disabled, so set enabled flag.
                plan_activity_for_milestone.enabled = True

                # Now move the activity to the swimlane and position it
                plan_activity_for_milestone.swimlane = swimlane
                plan_activity_for_milestone.track_number = track_number

                plan_activity_for_milestone.save()


    def add_delete_activities(self, level:int, swimlane:SwimlaneForVisual, delete_flag:bool):
        """
        Selects activities (not milestones) from the plan at the specified level and adds them or deletes them to/from the visual.
        Level 0 implies all activities.

        :param level:
        :param swimlane:
        :param delete_flag:
        :return:
        """
        # If delete_flag is set then simply set the disabled flag on all the activities in the visual at the specified level
        if delete_flag:
            visual_activities = swimlane.get_visual_activities()
            for visual_activity in visual_activities:
                # Check whether plan activity for this visual activity has the right level
                plan_activity_for_visual_activity = self.plan_activities.filter(unique_sticky_activity_id=visual_activity.unique_id_from_plan)[0]

                if level == 0 or plan_activity_for_visual_activity.level == level:
                    visual_activity.enabled = False
                    visual_activity.save()
            return

        # Get all the activities from the plan at the specified level
        plan_activities = self.plan_activities.filter(level=level, milestone_flag=False)

        # We want to know which activities are already in the visual and enabled.
        # ToDo: Re-factor this snippet, it uses different ways to get similar data (activities for visual)
        visual_activities = self.visual_for_plan.get_visual_activities(to_dict=False, include_disabled=False)
        disabled_activities = self.visual_for_plan.visualactivity_set.filter(enabled=False)
        enabled_ids_from_visual = [visual_activity.unique_id_from_plan for visual_activity in visual_activities]
        disabled_ids_from_visual = [visual_activity.unique_id_from_plan for visual_activity in disabled_activities]

        for activity in plan_activities:
            # There are three cases:
            # 1. The activity is already in the visual and enabled.  In this case we do nothing.
            # 2. The activity is already in the visual but disabled.  In this case we enable it and move to unused track.
            # 3. The activity is not in the visual.  In this case we add it.

            # Select the track number where this activity will go.
            track_number = swimlane.get_next_unused_track_number()

            if activity.unique_sticky_activity_id in enabled_ids_from_visual:
                # The activity is already in the visual and enabled so do nothing.
                continue

            if activity.unique_sticky_activity_id in disabled_ids_from_visual:
                # The visual already exists but has been disabled so re-enable, switch to this swimlane and set track number.
                visual_activity = self.visual_for_plan.visualactivity_set.filter(unique_id_from_plan=activity.unique_sticky_activity_id)[0]
                visual_activity.enabled = True
                visual_activity.swimlane = swimlane
                visual_activity.vertical_positioning_value = track_number
                visual_activity.save()
                continue

            # The activity is not already in the visual so add it.
            VisualActivity.objects.create(
                visual=self.visual_for_plan,
                swimlane=swimlane,
                unique_id_from_plan=activity.unique_sticky_activity_id,
                enabled=True,
                plotable_shape=self.visual_settings.default_activity_shape,
                vertical_positioning_value=track_number,
                height_in_tracks=1,
                text_horizontal_alignment=VisualActivity.HorizontalAlignment.CENTER,
                text_vertical_alignment=VisualActivity.VerticalAlignment.MIDDLE,
                text_flow=VisualActivity.TextFlow.FLOW_TO_RIGHT,
                plotable_style=self.visual_settings.default_activity_plotable_style,
            )

    @staticmethod
    def sort_swimlane(swimlane, start_track=2):
        """
        Sort all the activities within a swimlane by start date and place each activity on a different track
        :param swimlane:
        :return:
        """

        track_number = start_track  # Leave one track for swimlane heading by default.

        # Carry out join on plan activity to get start date, using subquery.
        activities = (VisualActivity.objects.annotate(start_date=Subquery(PlanActivity.objects.filter(
            plan_id=OuterRef('visual__plan_id'),
            unique_sticky_activity_id=OuterRef('unique_id_from_plan')).values('start_date')))
                      .filter(visual_id=swimlane.plan_visual_id, swimlane_id=swimlane.id, enabled=True)).order_by('start_date')
        for visual_activity in activities:
            visual_activity.vertical_positioning_value = track_number
            visual_activity.save()
            track_number += 1

    @staticmethod
    def compress_swimlane(swimlane, start=2):
        """
        Compresses a swimlane by removing any blank tracks between activities. First track specified by start.
        :param swimlane:
        :return:
        """
        # Get all the activities from the visual for this swimlane, ordered by track number
        activities = swimlane.get_visual_activities().order_by('vertical_positioning_value')

        # The activities are in vertical position order, so the approach will be to go through the activities
        # and re-position them to the appropriate track.

        target_track_number = start-1
        current_track_number = 0

        with transaction.atomic():
            for activity in activities:
                if activity.vertical_positioning_value > current_track_number:
                    current_track_number = activity.vertical_positioning_value
                    target_track_number += 1

                activity.vertical_positioning_value = target_track_number
                activity.save()

    def add_activities_to_swimlane(self, activity_ids: List[str], swimlane_sequence_number: int):
        """
        Accepts a list of plan activities and adds each to the end of the swimlane at the specified sequence number for
        this visual.

        :param activities:
        :param swimlane_sequence_number:
        :return:
        """
        for activity_id in activity_ids:
            self.add_activity_to_swimlane(activity_id, swimlane_sequence_number)

    def add_activity_to_swimlane(self, activity_unique_id: str, swimlane_sequence_number: int):
        """
        Adds a single activity to the end of the swimlane at the specified sequence number for this visual.
        Takes account of different cases:

        CASE 1: Activity isn't in visual
        - Add to visual at bottom of swimlane (as usual)

        CASE 2: Activity is in visual but in another swimlane
        - Remove from other swimlane
        - Compress other swimlane
        - Add back to new swimlane

        CASE 3: Activity is in visual and in this swimlane
        - Assume the user wants the sub-activities together, so move existing activities together at bottom
        - Change track to last plus one in the swimlane
        - Compress swimlane (as may be a gap where the activity was)

        :param activity:
        :param swimlane_sequence_number:
        :return:
        """
        # I don't know whether this is the right way to do this!
        #
        # The logic is that I want to add this activity from the plan to the supplied visual.  But if I have previously
        # added the activity to the visual and then removed it there will already be a record for this activity with the
        # enabled flag set to False.
        #
        # This means that I don't always want to create a new record.  I think in practice the keys which define the
        # Visual Activity should be included in the URL not the additional data.  As I don't have any other data to add
        # then the data element of the PUT request will be empty.  I don't know whether that is seen as poor practice
        # or not, but it avoids using GET incorrectly or having to access data before validation which seems wrong.
        #
        # Note - the above means we don't even need a serializer (which seems a bit wrong).

        # Get swimlane where we want to place this activity
        swimlane = self.visual_for_plan.get_swimlane_by_sequence_number(swimlane_sequence_number)

        try:
            visual_activity = self.visual_for_plan.visualactivity_set.get(unique_id_from_plan=activity_unique_id)
        except VisualActivity.DoesNotExist:
            # Need to create a new record for this activity in this visual.

            # if the plan activity for this visual activity is a milestone, plot as DIAMOND, else plot as RECTANGLE
            plan_activity = self.visual_for_plan.plan.planactivity_set.get(unique_sticky_activity_id=activity_unique_id)
            if plan_activity.milestone_flag is True:
                initial_plotable_shape = self.visual_for_plan.default_milestone_shape
                initial_plotable_style = self.visual_for_plan.default_milestone_plotable_style
            else:
                initial_plotable_shape = self.visual_for_plan.default_activity_shape
                initial_plotable_style = self.visual_for_plan.default_activity_plotable_style

            new_visual_activity = VisualActivity(
                visual=self.visual_for_plan,
                unique_id_from_plan=activity_unique_id,
                vertical_positioning_value=swimlane.get_next_unused_track_number(),
                height_in_tracks=DEFAULT_HEIGHT_IN_TRACKS,
                text_horizontal_alignment=DEFAULT_TEXT_HORIZONTAL_ALIGNMENT,
                text_vertical_alignment=DEFAULT_TEXT_VERTICAL_ALIGNMENT,
                text_flow=DEFAULT_TEXT_FLOW,
                plotable_shape=initial_plotable_shape,
                plotable_style=initial_plotable_style,
                swimlane_id=swimlane.id,
                enabled=True
            )
            new_visual_activity.save()
            status = ServiceResponse(
                status=ServiceStatusCode.SUCCESS,
                message=f"New activity added to visual {self.visual_for_plan} for Id = {activity_unique_id}",
                data= {'visual_activity': new_visual_activity}
            )
            return status
        else:
            # There is already a record so we need to change the enabled flag to true.
            # Also don't want to retain vertical position as something else may be placed there.
            # Also need to update swimlane to one supplied.
            visual_activity.enabled = True
            visual_activity.vertical_positioning_value = swimlane.get_next_unused_track_number()
            visual_activity.swimlane_id = swimlane.id

            visual_activity.save()
            status = ServiceResponse(
                status=ServiceStatusCode.SUCCESS,
                message=f"Existing activity re-added to visual {self.visual_for_plan} for Id = {activity_unique_id} in swimlane {swimlane_sequence_number}",
                data= {'visual_activity': visual_activity}
            )
            return status

    def add_subactivities(self, unique_activity_id, swimlane_sequence_num):
        sub_activity_ids: List[str] = [activity.unique_sticky_activity_id for activity in self.plan_tree.get_plan_tree_child_activities_by_unique_id(unique_activity_id)]

        self.add_activities_to_swimlane(sub_activity_ids, swimlane_sequence_num)

        status = ServiceResponse(
            status=ServiceStatusCode.SUCCESS,
            message=f"{len(sub_activity_ids)} sub-activities under id {unique_activity_id} added to visual {self.visual_for_plan} in swimlane {swimlane_sequence_num}",
            data={'visual_activity_ids_added': sub_activity_ids}
        )
        return status

    @classmethod
    def create_full_visual(cls, plan: Plan):
        """
        Use algorithm to create a full visual from the plan.
        :return:
        """
        layout_options = LayoutOptions(
            max_lanes=5,
            max_tracks_per_lane=8,
            reserve_track_zero=True,
            milestones_lane_name="Milestones",
            label_window_start=None,
            label_window_end=None
        )
        plan_tree = plan.get_plan_tree()
        auto_layout = build_initial_layout(plan_tree, options=layout_options)

        auto_visual: PlanVisual = PlanVisual.objects.create_with_defaults(plan=plan)


        # Now add the activities to the visual
        for lane in auto_layout["lanes"]:
            swimlanes = auto_visual.add_swimlanes_to_visual(
                auto_visual.default_swimlane_plotable_style, lane["name"]
            )
            swimlane = swimlanes[0]

            for track_records in lane["tracks"]:
                # Allow for activity record being None (need to fix so it doesn't happen!)
                # ToDo: Fix at source so that lane['tracks'] doesn't include None values
                if track_records is None:
                    continue
                for activity_record in track_records:
                    plan_activity: PlanActivity = activity_record['activity']
                    flow = activity_record['label_side']
                    visual_activity_shape = \
                        auto_visual.default_activity_shape if plan_activity.milestone_flag is False \
                            else auto_visual.default_milestone_shape
                    text_flow = VisualActivity.TextFlow.FLOW_TO_RIGHT if flow == "left" else VisualActivity.TextFlow.FLOW_TO_LEFT
                    try:
                        VisualActivity.objects.create(
                            visual=auto_visual,
                            unique_id_from_plan=plan_activity.unique_sticky_activity_id,
                            enabled=True,
                            swimlane=swimlane,
                            plotable_shape=visual_activity_shape,
                            vertical_positioning_value=activity_record['track_index'],
                            height_in_tracks=1,
                            text_horizontal_alignment=VisualActivity.HorizontalAlignment.CENTER,
                            text_vertical_alignment=VisualActivity.VerticalAlignment.MIDDLE,
                            text_flow=text_flow,
                            plotable_style=auto_visual.default_activity_plotable_style,
                        )
                    except IntegrityError as e:
                        logger.warning(f"Activity already exists for plan activity {plan_activity.unique_sticky_activity_id}")
        return auto_visual