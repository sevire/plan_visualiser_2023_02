import logging

from plan_visual_django.services.plan_file_utilities.plan_field import PlanFieldEnum, PlanFieldNameEnum

logger = logging.getLogger(__name__)


def update_plan_activity(plan, activity, action):
    """
    NOTE - the following is a temporary hack.
    ToDo: Refactor to more generically handle the mapping of the input data to the plan fields for milestones.
    If the input file includes a milestone flag then use that to set the milestone flag in the plan.
    If not then use the duration to set the milestone flag.

    If update_flag is True then we are updating an existing record.

    :param plan:
    :param activity:
    :param update_flag:
    :return:
    """

    # Check for delete action first as no point doing anything else if no record.
    from plan_visual_django.models import PlanActivity
    if action == "delete":
        deleted_sticky_id = activity['unique_sticky_activity_id']
        # Remove from plan
        record = PlanActivity.objects.get(plan=plan, unique_sticky_activity_id=deleted_sticky_id)
        record.delete()

        # Remove from visuals
        from plan_visual_django.models import PlanVisual, VisualActivity
        visuals = PlanVisual.objects.filter(plan=plan)
        for visual in visuals:
            visual_activities = VisualActivity.objects.filter(visual=visual, unique_id_from_plan=deleted_sticky_id)
            for visual_activity in visual_activities:
                visual_activity.delete()
    else:
        if PlanFieldNameEnum.MILESTONE_FLAG.value in activity:
            milestone_flag = activity[PlanFieldNameEnum.MILESTONE_FLAG.name]
        else:
            if activity[PlanFieldNameEnum.DURATION.value] == 0:
                milestone_flag = True
            else:
                milestone_flag = False

        if action == "update":
            record = PlanActivity.objects.get(plan=plan, unique_sticky_activity_id=activity['unique_sticky_activity_id'])
            record.activity_name = activity['activity_name']
            record.duration = activity['duration']
            record.start_date = activity['start_date']
            record.end_date = activity['end_date']
            record.level = activity['level'] if 'level' in activity else 1
            record.sequence_number = activity['sequence_number']

            record.save()
        elif action == "add":
            record = PlanActivity.objects.create(
                plan=plan,
                unique_sticky_activity_id=activity['unique_sticky_activity_id'],
                activity_name=activity['activity_name'],
                milestone_flag=milestone_flag,
                start_date=activity['start_date'],
                end_date=activity['end_date'],
                level=activity['level'] if 'level' in activity else 1,
                sequence_number=activity['sequence_number'],
            )


def parse_plan_file(raw_data, headers, file_reader, plan_field_mapping):
    parsed_data = file_reader.parse(raw_data, headers, plan_field_mapping=plan_field_mapping)
    return parsed_data


def read_plan_file(plan, file_reader):
    raw_data, headers = file_reader.read(plan)
    return raw_data, headers


def read_and_parse_plan(plan, plan_field_mapping, file_reader, update_flag=False):
    """
    Reads and parses the uploaded plan in order to store plan within the database.

    If the plan is a new upload we add all (valid) records to the database.

    If the plan is a re-upload of an existing plan then we need to work out what has changed and make updates
    accordingly, which means:
    - Adding new activities to the plan_activity table in the database
    - Where an activity has been deleted, delete it from the plan_activity table in the database
    - Where an activity has been modified, update the plan_activity table in the database to reflect the changes.

    We use the unique_sticky_id in the plan to match records from the current plan to the new plan. This requires
    that activities retain the same ID within the source file which represents the plan.

    :param plan:
    :param plan_field_mapping:
    :param file_reader:
    :param update_flag:
    :return:
    """
    logger.debug(f'Reading plan: {plan}')
    raw_data, headers = read_plan_file(plan, file_reader)
    parsed_data = parse_plan_file(
        raw_data=raw_data,
        headers=headers,
        plan_field_mapping=plan_field_mapping,
        file_reader=file_reader
    )

    # Allocate sequence numbers to the activities.  Then if this is a re-upload as we go through the different
    # types of update, we apply the new sequence number as needed.
    for sequence_number, activity in enumerate(parsed_data, start=1):
        activity['sequence_number'] = sequence_number

    if update_flag is False:
        # This is a new plan file so we simply add all records to the plan_activity table.
        for activity in parsed_data:
            update_plan_activity(plan, activity=activity, action="add")
    else:
        new_activities, updated_activities, deleted_sticky_ids = analyse_plan_changes(parsed_data, plan)
        for activity in new_activities:
            update_plan_activity(plan, activity=activity, action="add")
        for activity in updated_activities:
            update_plan_activity(plan, activity=activity, action="update")
        for deleted_sticky_id in deleted_sticky_ids:
            # We don't have an activity (as it's gone from the plan) so create dummy one to pass unique id for deletion
            activity = {'unique_sticky_activity_id': deleted_sticky_id}
            update_plan_activity(plan, activity=activity, action="delete")
            # Need to remove from the plan and from any visuals


def analyse_plan_changes(new_parsed_activity_data, plan):
    """
    Takes the activities from a new version of an existing plan and applies changes to the plan.

    :param new_parsed_activity_data:
    :return:
    """
    from plan_visual_django.models import PlanActivity
    current_plan_sticky_ids = PlanActivity.objects.filter(plan=plan).values_list('unique_sticky_activity_id', flat=True)
    new_plan_sticky_ids = [activity['unique_sticky_activity_id'] for activity in new_parsed_activity_data]

    new_activities = [activity for activity in new_parsed_activity_data if activity['unique_sticky_activity_id'] not in current_plan_sticky_ids]
    updated_activities = [activity for activity in new_parsed_activity_data if activity['unique_sticky_activity_id'] in current_plan_sticky_ids]
    deleted_activity_sticky_ids = [sticky_id for sticky_id in current_plan_sticky_ids if sticky_id not in new_plan_sticky_ids]
    return new_activities, updated_activities, deleted_activity_sticky_ids


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

    num_activities = activities.count()
    num_milestones = milestones.count()

    if num_activities == 0:
        earliest_start_date = None
        latest_end_date = None
        duration = None
        levels = None
    else:
        earliest_activity = activities.order_by('start_date').first()
        earliest_start_date = earliest_activity.start_date if earliest_activity else None

        latest_activity = activities.order_by('-end_date').first()
        latest_end_date = latest_activity.end_date if latest_activity else None

        duration = latest_end_date - earliest_start_date
        levels = activities.values('level').distinct().count()

    return {
        'plan_file_name': ("Last uploaded file name", plan.file_name),
        'number_of_activities': ("# Activities", num_activities),
        'number_of_milestones': ("# Milestones", num_milestones),
        'earliest_start_date': ("Earliest date", earliest_start_date),
        'latest_end_date': ("Latest date", latest_end_date),
        'duration': ("Plan Duration", duration),
        'levels': ("# Levels", levels),
    }
