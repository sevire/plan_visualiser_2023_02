def parse_plan(plan, plan_file, mapping_type, file_reader):
    raw_data = file_reader.read(plan_file)
    parsed_data = file_reader.parse(raw_data, plan_field_mapping=mapping_type)
    for activity in parsed_data:
        # Note that the duration field isn't stored, but used to work out whether the activity is a
        # milestone.
        if activity['duration'] == 0:
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
