from plan_visual_django.models import SwimlaneForVisual
import logging

logger = logging.getLogger()

def adjust_visual_activity_track(visual_activity, swimlane_id):
    """
    There are various scenarios where we need to auto-adjust the track which a visual activity is placed.

    Two common uses cases are:
    - When moving activities between swimlanes, we want the activity to sit below the existing activities in that
      swimlane, not just occupy the same track as it was placed in its original swimlane
    - Similarly, when re-enabling an activity, which was previously disabled, we want to (usually) re-position it to the bottom
      of the swimlane.

    So this will take an existing visual activity record, and a target swimlane id, and then
    - Find the track which is below the bottommost occupied track for the target swimlane
    - Update the swimlane to the target swimlane
    - Update the track to be the calculated track

    Note that the record isn't saved, it's just update here, the caller will then do whatever is required
    next.

    :return:
    """
    try:
        swimlane = SwimlaneForVisual.objects.get(id=swimlane_id)
    except SwimlaneForVisual.DoesNotExist:
        logger.warning(f"Can't move activity to swimlane - swimlane with id {swimlane_id} doesn't exist")
    else:
        new_track = swimlane.get_next_unused_track_number()
        visual_activity.vertical_positioning_value = new_track
        visual_activity.swimlane = swimlane

