from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.generics import ListAPIView
from api.v1.model.visual.plotable_style.serializer import ModelVisualStyleSerializer
from plan_visual_django.models import PlotableStyle
from django.conf import settings

class ModelVisualStyleAPI(ListAPIView):
    def get(self, request, **kwargs):
        user = request.user
        shared_data_user = User.objects.get(username=settings.SHARED_DATA_USER_NAME)
        style_queryset = PlotableStyle.objects.filter(user__in=[user, shared_data_user])

        serializer = ModelVisualStyleSerializer(instance=style_queryset, many=True)

        response = serializer.data
        return JsonResponse(response, safe=False)
