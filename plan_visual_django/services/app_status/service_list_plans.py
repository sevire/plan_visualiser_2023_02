from django.contrib.auth import get_user_model

from plan_visual_django.models import Plan

User = get_user_model()

def service_list_plans():
    users = User.objects.all()

    plan_data_by_user = []

    for user in users:
        plans = Plan.objects.filter(user=user)

        for plan in plans:
            plan_record = {
                'user': user.username,
                'plan_name': plan.plan_name,
            }
            plan_data_by_user.append(plan_record)

    return plan_data_by_user
