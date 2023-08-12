"""
Includes algorithms for automatic layout of the plan.

The main algorithm is the following:
1. All milestones in a single swimlane laid out chronologically.
2. Creating swimlanes and activities by using the structure of the plan. (that is Level information).
"""
from plan_visual_django.models import SwimlaneForVisual, VisualActivity
from plan_visual_django.services.general.date_utilities import proportion_between_dates
from plan_visual_django.services.visual.visual_settings import VisualSettings


class VisualAutoLayoutManager:
    def __init__(self, visual_for_plan):
        self.visual_for_plan = visual_for_plan
        self.plan = visual_for_plan.plan
        self.plan_activities = self.plan.planactivity_set.all()

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
        swimlane = SwimlaneForVisual.objects.create(
            plan_visual=self.visual_for_plan,
            swim_lane_name="Milestones",
            plotable_style=swimlane_plotable_style,
            sequence_number=500
        )
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
            track_number = index + 1

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
