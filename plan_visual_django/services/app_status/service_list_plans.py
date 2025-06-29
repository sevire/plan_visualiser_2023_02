from django.contrib.auth import get_user_model

from plan_visual_django.models import Plan

User = get_user_model()

def service_list_plans():
    users = User.objects.all()

    plan_data_by_user = []

    for user in users:
        plans = Plan.objects.filter(user=user)

        for plan in plans:
            plan_data = plan.get_plan_summary_data()
            plan_data_as_dict = {key_from_tuple: value for key, (key_from_tuple, value) in plan_data.items()}
            plan_record = {
                'user': user.username,
            }
            plan_record.update(plan_data_as_dict)
            plan_data_by_user.append(plan_record)

    return plan_data_by_user
