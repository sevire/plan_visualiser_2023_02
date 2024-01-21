import logging

logger = logging.getLogger(__name__)

def parse_activity(plan, activity):
    # NOTE - the following is a temporary hack.
    # ToDo: Refactor to more generically handle the mapping of the input data to the plan fields for milestones.
    # If the input file includes a milestone flag then use that to set the milestone flag in the plan.
    # If not then use the duration to set the milestone flag.

    from plan_visual_django.models import PlanField
    if PlanField.PlanFieldName.MILESTONE_FLAG in activity:
        milestone_flag = activity[PlanField.PlanFieldName.MILESTONE_FLAG]
    else:
        if activity[PlanField.PlanFieldName.DURATION] == 0:
            milestone_flag = True
        else:
            milestone_flag = False

    from plan_visual_django.models import PlanActivity
    record = PlanActivity(
        plan=plan,
        unique_sticky_activity_id=activity['unique_sticky_activity_id'],
        activity_name=activity['activity_name'],
        milestone_flag=milestone_flag,
        start_date=activity['start_date'],
        end_date=activity['end_date'],
        level=activity['level'] if 'level' in activity else 1,
    )
    return record


def parse_plan_file(raw_data, headers, file_reader, plan_field_mapping):
    parsed_data = file_reader.parse(raw_data, headers, plan_field_mapping=plan_field_mapping)
    return parsed_data


def read_plan_file(plan, file_reader):
    raw_data, headers = file_reader.read(plan)
    return raw_data, headers


def read_and_parse_plan(plan, plan_field_mapping, file_reader):
    logger.debug(f'Reading plan: {plan}')
    raw_data, headers = read_plan_file(plan, file_reader)
    parsed_data = parse_plan_file(
        raw_data=raw_data,
        headers=headers,
        plan_field_mapping=plan_field_mapping,
        file_reader=file_reader
    )

    for activity in parsed_data:
        record = parse_activity(plan, activity=activity)
        record.save()


def extract_summary_plan_info(plan) -> dict:
    """
    Extracts summary information from the plan. This is used to populate the plan summary page.

    Data included in extract is:
    - Number of activities
    - Number of milestones
    - Earliest start date
    - Latest end date
    - Duration of plan
    - Number of activities per level


    :param plan:
    :return:
    """
    from plan_visual_django.models import PlanActivity
    activities = PlanActivity.objects.filter(plan=plan)
    milestones = activities.filter(milestone_flag=True)
    earliest_start_date = activities.order_by('start_date').first().start_date
    latest_end_date = activities.order_by('-end_date').first().end_date
    duration = latest_end_date - earliest_start_date
    levels = activities.values('level').distinct().count()

    return {
        'plan_file_name': ("Last uploaded file name", plan.file_name),
        'number_of_activities': ("# Activities", activities.count()),
        'number_of_milestones': ("# Milestones", milestones.count()),
        'earliest_start_date': ("Earliest date", earliest_start_date),
        'latest_end_date': ("Latest date", latest_end_date),
        'duration': ("Plan Duration", duration),
        'levels': ("# Levels", levels),
    }
