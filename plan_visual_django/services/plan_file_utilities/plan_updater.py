from plan_visual_django.models import PlanActivity


def update_plan_data(new_parsed_activity_data, plan):
    """
    Takes the activities from a new version of an existing plan and applies changes to the plan.

    :param new_parsed_activity_data:
    :return:
    """
    current_plan_sticky_ids = PlanActivity.objects.filter(plan=plan).values_list('unique_sticky_activity_id', flat=True)
    new_plan_sticky_ids = [activity['unique_sticky_activity_id'] for activity in new_parsed_activity_data]

    new_activities = [activity for activity in new_parsed_activity_data if activity['unique_sticky_activity_id'] not in current_plan_sticky_ids]
    updated_activities = [activity for activity in new_parsed_activity_data if activity['unique_sticky_activity_id'] in current_plan_sticky_ids]
    deleted_activity_sticky_ids = [sticky_id for sticky_id in current_plan_sticky_ids if sticky_id not in new_plan_sticky_ids]

    return new_activities, updated_activities, deleted_activity_sticky_ids