"""
Includes algorithms for automatic layout of the plan.

The main algorithm is the following:
1. All milestones in a single swimlane laid out chronologically.
2. Creating swimlanes and activities by using the structure of the plan. (that is Level information).
"""
from django.db import IntegrityError
from django.db.models import Subquery, OuterRef

from plan_visual_django.exceptions import DuplicateSwimlaneException
from plan_visual_django.models import SwimlaneForVisual, VisualActivity, PlanVisual, PlanActivity
from plan_visual_django.services.general.date_utilities import proportion_between_dates
from plan_visual_django.services.visual.visual_settings import VisualSettings


class VisualAutoLayoutManager:
    def __init__(self, visual_id_for_plan):
        self.visual_for_plan = PlanVisual.objects.get(id=visual_id_for_plan)
        self.plan = self.visual_for_plan.plan
        self.plan_activities = self.plan.planactivity_set.all()  # Note this creates a queryset which may be modified.
        self.visual_settings = VisualSettings(visual_id_for_plan)

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
                    vertical_positioning_type=VisualActivity.VerticalPositioningType.TRACK_NUMBER,
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
                vertical_positioning_type=VisualActivity.VerticalPositioningType.TRACK_NUMBER,
                vertical_positioning_value=track_number,
                height_in_tracks=1,
                text_horizontal_alignment=VisualActivity.HorizontalAlignment.CENTER,
                text_vertical_alignment=VisualActivity.VerticalAlignment.MIDDLE,
                text_flow=VisualActivity.TextFlow.FLOW_TO_RIGHT,
                plotable_style=self.visual_settings.default_activity_plotable_style,
            )

    def sort_swimlane(self, swimlane):
        """
        Sort all the activities within a swimlane by start date and place each activity on a different track
        :param swimlane:
        :return:
        """
        track_number = 1

        # Carry out join on plan activity to get start date, using subquery.
        activities = (VisualActivity.objects.annotate(start_date=Subquery(PlanActivity.objects.filter(
            plan_id=OuterRef('visual__plan_id'),
            unique_sticky_activity_id=OuterRef('unique_id_from_plan')).values('start_date')))
                      .filter(visual_id=swimlane.plan_visual_id)).order_by('start_date')
        for visual_activity in activities:
            visual_activity.vertical_positioning_value = track_number
            visual_activity.save()
            track_number += 1

    def compress_swimlane(self, swimlane):
        """
        Compresses a swimlane by removing any blank tracks between activities.
        :param swimlane:
        :return:
        """
        # Get all the activities from the visual for this swimlane, ordered by track number
        activities = swimlane.get_visual_activities().order_by('vertical_positioning_value')

        # Now go through the activities and if there is a gap between the current activity and the previous one
        # then move the current activity up to the previous one.
        previous_activity = None
        for activity in activities:
            if previous_activity is None:
                previous_activity = activity
                continue

            if activity.vertical_positioning_value > previous_activity.vertical_positioning_value + 1:
                # There is a gap between the current activity and the previous one so move the current activity up
                # to the previous one.
                activity.vertical_positioning_value = previous_activity.vertical_positioning_value + 1
                activity.save()

            previous_activity = activity
