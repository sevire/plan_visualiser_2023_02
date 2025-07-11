from django.db import transaction
from django.http import JsonResponse
from django.views import View
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from api.v1.model.visual.swimlane.serializer import ModelVisualSwimlaneListSerialiser, ModelVisualSwimlaneSerialiser
from plan_visual_django.models import PlanVisual, SwimlaneForVisual

class SwimlaneListViewDispatcher(View):
    @staticmethod
    def get(request, *args, **kwargs):
        view = ModelVisualSwimlaneListAPI.as_view()
        return view(request, *args, **kwargs)

    @staticmethod
    def patch(request, *args, **kwargs):
        view = ModelVisualSwimlaneUpdateAPI.as_view()
        return view(request, *args, **kwargs)


class ModelVisualSwimlaneListAPI(ListAPIView):
    def get(self, request, visual_id=None, **kwargs):
        visual_swimlanes_queryset = PlanVisual.objects.get(id=visual_id).swimlaneforvisual_set.all()
        serializer = ModelVisualSwimlaneListSerialiser(instance=visual_swimlanes_queryset, many=True)

        response = serializer.data

        return JsonResponse(response, safe=False)


class ModelVisualSwimlaneAPI(APIView):
    @staticmethod
    def get(request, visual_id, swimlane_seq_num, **kwargs):
        visual_swimlane_queryset = PlanVisual.objects.get(id=visual_id).swimlaneforvisual_set.get(sequence_number=swimlane_seq_num)
        serializer = ModelVisualSwimlaneListSerialiser(instance=visual_swimlane_queryset)

        response = serializer.data

        return JsonResponse(response, safe=False)


class ModelVisualSwimlaneUpdateAPI(APIView):
    """
    Updates some or all of multiple swimlane records for a given visual.

    While the id (Primary Key) of each swimlane will be provided, this endpoint will validate that each id sits within
    the supplied visual.
    """
    @staticmethod
    def patch(request, visual_id=None, **kwargs):
        """
        Applies updates to several swimlane records.  Only supplied fields will be updated for each record.

        Need to take account of the unique constraint for visual id / sequence number. It will be common to move the
        sequence around and this will involve updating the sequence number several swimlane records in the same update.
        Note that it is only permissable to swap sequence numbers around, so the received data must represent changes
        in sequence number in such a way that there is a temporary clash only with other records being updated in this
        update, and also that the records for which there is a clash are also being updated in this update so that after
        all updates are complete there is no clash.

        We will adopt the approach of not saving any changes to records which have an update to sequence number until
        all such changes have been made.  That way, as long as the combined impact of the updates doesn't result in a
        clash, when we save there won't be an error.

        :param request:
        :param visual_id:
        :param kwargs:
        :return:
        """
        swimlane_data = request.data

        updates_with_no_sequence_number = [swimlane_record for swimlane_record in swimlane_data if "sequence_number" not in swimlane_record]
        updates_with_sequence_number = [swimlane_record for swimlane_record in swimlane_data if "sequence_number" in swimlane_record]

        updates_dict = {item["id"]: item["sequence_number"] for item in updates_with_sequence_number}

        # All saves to be in a single transaction. The contract is to apply all updates or none.
        with transaction.atomic():

            # First deal with all the updates which don't include an update to sequence number.
            for swimlane_update_record in updates_with_no_sequence_number:
                try:
                    instance = SwimlaneForVisual.objects.get(id=swimlane_update_record['id'])
                    if instance.plan_visual_id != visual_id:
                        return Response({"error": f"Supplied swimlane ids do not belong to supplied visual"},
                                        status=status.HTTP_400_BAD_REQUEST)
                    serializer_for_current_record = ModelVisualSwimlaneSerialiser(instance, data=swimlane_update_record, partial=True)
                    if serializer_for_current_record.is_valid(raise_exception=True):
                        serializer_for_current_record.save()
                except SwimlaneForVisual.DoesNotExist:
                    return Response({"error": f"Object with id={swimlane_update_record['id']} not found"}, status=status.HTTP_400_BAD_REQUEST)

            # For the updates which include sequnce number, apply updates to object but don't save until all changes made.
            objects_with_sequence_number_updates = [SwimlaneForVisual.objects.get(id=record['id']) for record in updates_with_sequence_number]
            for swimlane_update_record in updates_with_sequence_number:
                try:
                    instance = SwimlaneForVisual.objects.get(id=swimlane_update_record['id'])

                    if instance.plan_visual_id != visual_id:
                        return Response({"error": f"Supplied swimlane ids do not belong to supplied visual"},
                                        status=status.HTTP_400_BAD_REQUEST)
                    existing_item = SwimlaneForVisual.objects.filter(plan_visual_id=visual_id).filter(sequence_number=swimlane_update_record["sequence_number"]).first()
                    if existing_item is None:
                        serializer_for_current_record = ModelVisualSwimlaneSerialiser(instance, data=swimlane_update_record, partial=True)
                        if serializer_for_current_record.is_valid(raise_exception=True):
                            serializer_for_current_record.save()
                    elif existing_item.id in updates_dict:
                        temp_sequence_number = -1  # Assign intermediate value
                        existing_item.sequence_number = temp_sequence_number
                        existing_item.save()
                        serializer_for_current_record = ModelVisualSwimlaneSerialiser(instance, data=swimlane_update_record, partial=True)
                        if serializer_for_current_record.is_valid(raise_exception=True):
                            serializer_for_current_record.save()
                    else:
                        raise ValueError(
                            f'Attempt to update sequence_number {swimlane_update_record["sequence_number"]} would violate unique constraint.')
                except SwimlaneForVisual.DoesNotExist:
                    return Response({"error": f"Object with id={swimlane_update_record['id']} not found"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)


class ModelVisualSwimlaneCompress(APIView):
    @staticmethod
    def post(request, visual_id, swimlane_seq_num, **kwargs):
        from plan_visual_django.services.visual.model.auto_layout import VisualAutoLayoutManager
        layout_manager = VisualAutoLayoutManager(visual_id)

        visual = PlanVisual.objects.get(id=visual_id)
        swimlane = visual.get_swimlane_by_sequence_number(swimlane_seq_num)
        layout_manager.compress_swimlane(swimlane)
        return Response(status=status.HTTP_200_OK)
