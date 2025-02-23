from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import generics
from plan_visual_django.models import PlotableStyle
from plan_visual_django.services.auth.user_services import CurrentUser
from api.v1.model.visual.plotable_style.serializer import ModelVisualStyleSerializer
from django.db.models import Q

User = get_user_model()


class ModelVisualStyleAPI(generics.ListAPIView):
    serializer_class = ModelVisualStyleSerializer

    def get_queryset(self):
        current_user = CurrentUser(self.request)
        shared_user = User.objects.get(username=settings.SHARED_DATA_USER_NAME)

        if current_user.is_authenticated():
            # Both user's and shared user's records
            return PlotableStyle.objects.filter(Q(user=current_user.user) | Q(user=shared_user))
        else:
            # Only shared user's records
            return PlotableStyle.objects.filter(user=shared_user)