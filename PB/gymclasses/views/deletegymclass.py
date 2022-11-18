import datetime as dt
from datetime import datetime, timedelta
import pytz
import rest_framework.parsers
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
import rest_framework.parsers

from PB.utility import ValidateInt, ValidatePhoneNumber
from accounts.models import UserExtension, User
from gymclasses.models import GymClass, GymClassSchedule
from studios.models import Studio


# Create your views here.


class DeleteGymClass(APIView):
    '''
    edits a specific profile
    '''

    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args, **kwargs):

        gym_class = kwargs['gym_class']
        data = request.data

        try:
            gym_class = GymClass.objects.get(id=gym_class)
        except ObjectDoesNotExist:
            return Response({'error': 'Gym Class was not found'}, status=404)

        if "delete" in data and data['delete']:
            GymClassSchedule.objects.filter(parent_class_id=gym_class).delete()
            gym_class.delete()
        else:
            for item in GymClassSchedule.objects.filter(parent_class_id=gym_class):
                setattr(item, "is_cancelled", True)
                item.save()

        return Response({"success": True})
