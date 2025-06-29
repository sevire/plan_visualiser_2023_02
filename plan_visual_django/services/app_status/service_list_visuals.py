from django.contrib.auth import get_user_model
from plan_visual_django.models import Plan, PlanVisual

User = get_user_model()

def service_list_visuals():
    users = User.objects.all()

    visual_data = []

    users = User.objects.all()

    for user in users:
        plans = Plan.objects.filter(user=user)

        for plan in plans:
            visuals = PlanVisual.objects.filter(plan=plan)

            for visual in visuals:
                visual_record = {
                    'user': user.username,
                    'plan_name': plan.plan_name,
                    'visual_name': visual.name,
                    'visual_num_activities': visual.activity_count()
                }
                visual_data.append(visual_record)
    return visual_data
