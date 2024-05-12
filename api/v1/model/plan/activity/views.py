from django.http import JsonResponse
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from api.v1.model.plan.activity.serializer import ModelPlanActivityListSerialiser, ModelPlanActivitySerialiser, \
    ModelPlanActivityByVisualListSerialiser
from api.v1.model.visual.activity.serializer import ModelVisualActivityListSerialiser, ModelVisualActivitySerialiser
from plan_visual_django.models import Plan, PlanVisual


class ModelPlanActivityListAPI(ListAPIView):
    def get(self, request, id=None, **kwargs):
        plan = Plan.objects.get(id=id)

        plan_activities_queryset = plan.planactivity_set.all()
        serializer = ModelPlanActivityListSerialiser(plan_activities_queryset, many=True)

        return JsonResponse(serializer.data, safe=False)


class ModelPlanActivityByVisualListAPI(ListAPIView):
    def get(self, request, visual_id=None, **kwargs):
        # Accessing plan but from visual id, so include visual information
        visual = PlanVisual.objects.get(pk=visual_id)
        plan = visual.plan
        plan_id = plan.id
        plan = Plan.objects.get(id=plan_id)

        plan_activities_queryset = plan.planactivity_set.all()
        visual_activities_queryset = visual.visualactivity_set.all()

        # We now have all the plan activities and the visual activities for activities added to this visual
        # Combine them into single structure to be converted to JSON.
        # Doing this in multiline syntax but probably could to in a comprehension if not too complex.
        consolidated_activities = []
        for plan_activity in plan_activities_queryset:
            plan_activity_serializer = ModelPlanActivitySerialiser(plan_activity)
            activity_record = {'plan_data': plan_activity_serializer.data}
            matching_visual_activities = [visual_activity for visual_activity in visual_activities_queryset if visual_activity.unique_id_from_plan == plan_activity.unique_sticky_activity_id]

            # Should be either zero or one match
            if len(matching_visual_activities) > 0:
                visual_activity_serializer = ModelVisualActivitySerialiser(matching_visual_activities[0])
                activity_record['visual_data'] = visual_activity_serializer.data
            consolidated_activities.append(activity_record)

        return JsonResponse(consolidated_activities, safe=False)


class ModelPlanActivityAPI(APIView):
    def get(self, request, plan_id, unique_id):
        # ToDo: Is it right to go Plan --> Plan.activity_set or just do in one get
        plan = Plan.objects.get(id=plan_id)
        plan_activity_queryset = plan.planactivity_set.get(unique_sticky_activity_id=unique_id)

        serializer = ModelPlanActivitySerialiser(instance=plan_activity_queryset)

        response = serializer.data
        return JsonResponse(response, safe=False)
