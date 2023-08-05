from plan_visual_django.models import PlanVisual
from plan_visual_django.services.visual.renderers import VisualRenderer
from plan_visual_django.services.visual.visual_elements import Timeline, TimelineCollection, VisualElementCollection, \
    SwimlaneCollection, ActivityCollection
from plan_visual_django.services.visual.visual_settings import VisualSettings


class VisualOrchestration:
    """
    A class which manages the end to end creation of a visual, including:
    - The creation of each collection.
    - The management of the layout of each collection.
    - The passing of dependencies between collections and passing data between them.
    """
    def __init__(self, visual: PlanVisual, visual_settings:VisualSettings):
        self.plan_visual: PlanVisual = visual
        self.visual_settings = visual_settings
        self.visual_collection = VisualElementCollection()

        self.visual_activities = self.plan_visual.get_visual_activities()

        # We need to know the earliest start and latest end date from the activities as that will be used to drive the
        # calculation of the timelines.
        self.earliest_activity_start = min(activity["start_date"] for activity in self.visual_activities)
        self.latest_activity_end = max(activity["end_date"] for activity in self.visual_activities)

        self.create_visual()

    def create_visual(self):
        """
        This method creates a Plotable object for every element within the visual.

        The sequence of events in creating a visual is:
        1. Generate all the timelines as this sets the minimum and maximum date for the visual.
        2. Generate swimlanes, including the calculation of vertical positioning of each activity.
        3. Complete plotting of each activity.
        :return:
        """

        # Get all the timelines configured for this visual
        timeline_records = self.plan_visual.timelineforvisual_set.all()

        # Only create the timelines if there are any configured for this visual
        if timeline_records:
            timeline_settings = {
                "timeline_height": 10,
            }

            timelines = TimelineCollection(
                self.earliest_activity_start,
                self.latest_activity_end,
                timeline_records,
                timeline_settings
            )
            timelines.initialise_collection()
            timelines_collection = timelines.create_collection(visual_settings=self.visual_settings, timeline_settings=timeline_settings)
            _, height = timelines_collection.get_dimensions()
            top_offset = height

            self.visual_collection.add_collection(timelines_collection)

            visual_start_date = timelines.visual_start_date_final
            visual_end_date = timelines.visual_end_date_final
        else:
            visual_start_date = self.earliest_activity_start
            visual_end_date = self.latest_activity_end
            top_offset = 0

        swimlane_records = self.plan_visual.swimlaneforvisual_set.all()
        swimlane_settings = {}

        # We need to create the Activity Collection before working out the swimlanes because creating the swimlane
        # collection will include calculating the vertical positions for all the activities in the visual.
        activity_collection = ActivityCollection(
            visual_start_date,
            visual_end_date,
            self.visual_activities,
            self.visual_settings,
            0,
            self.visual_settings.width,
            0,
            self.visual_settings.height
        )
        activity_collection.initialise_collection()
        created_activity_collection = activity_collection.create_collection(
            visual_settings=self.visual_settings,
            collection_settings=None,
            top_offset=top_offset
        )

        swimlanes = SwimlaneCollection(
            visual_start_date,
            visual_end_date,
            swimlane_records,
            created_activity_collection,
            self.visual_settings,
            swimlane_settings
        )

        swimlanes.initialise_collection()
        swimlanes_collection = swimlanes.create_collection(visual_settings=self.visual_settings, collection_settings=None, top_offset=top_offset)

        self.visual_collection.add_collection(swimlanes_collection)
        self.visual_collection.add_collection(created_activity_collection)

        self.visual_collection.print_collection()
