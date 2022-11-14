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

KEYS = [
    'date'
]


class DeleteGymSchedule(APIView):
    '''
    edits a specific profile
    '''

    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    # permission_classes = [IsAuthenticated]

    def post(self, request: Request, *args, **kwargs):

        gym_class = kwargs['gym_class']
        data = request.data

        try:
            gym_class = GymClass.objects.get(id=gym_class)
        except ObjectDoesNotExist:
            return Response({'error': 'Gym Class was not found'}, status=404)

        errors = self.ValidateData(request.data)

        if len(errors):
            return Response(errors)

        gym_schedules = GymClassSchedule.objects.filter(parent_class_id=gym_class)
        date = datetime.strptime(data['date'], '%d/%m/%Y').date()

        is_delete = False
        for item in gym_schedules:
            if item.date == date:
                is_delete = True
                item.delete()

        if not is_delete:
            return Response({"Error": "No class schedule found to delete"})

        return Response({"success": True})

    def ValidateData(self, data) -> dict:
        errors = {}
        for key in KEYS:
            if key not in data:
                errors[key] = "Missing Key"

        if 'date' not in errors:
            try:
                datetime.strptime(data['date'], '%d/%m/%Y')
            except ValueError:
                errors['date'] = "Wrong Start Date Format"

        return errors
