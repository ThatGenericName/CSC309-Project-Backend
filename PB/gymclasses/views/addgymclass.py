import datetime as dt
from datetime import datetime, timedelta
from django.conf import settings
from django.utils.timezone import make_aware
import pytz
import rest_framework.parsers
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import validate_email
from django.utils import timezone
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
    'name',
    'coach',
    'enrollment_capacity',
    'description',
    'keywords',
    'start_date',
    'end_date',
    'day',
    'start_time',
    'end_time'
]


class CreateGymClass(APIView):
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

        studioId = kwargs['studio_id']
        data = request.data

        try:
            studio = Studio.objects.get(id=studioId)
        except ObjectDoesNotExist:
            return Response({'error': 'Studio was not found'}, status=404)

        try:
            coach = User.objects.get(id=data['coach'])
        except ObjectDoesNotExist:
            return Response({'error': 'Coach was not found'}, status=404)

        errors = self.ValidateData(request.data)

        if len(errors):
            return Response(errors)

        start_time = dt.datetime.strptime(data['start_time'], '%H:%M').time()
        end_time = dt.datetime.strptime(data['end_time'], '%H:%M').time()

        start_date = datetime.strptime(data['start_date'], '%d/%m/%Y')
        tz = pytz.timezone('America/Toronto')
        start_date = start_date.replace(tzinfo=tz)

        end_date = datetime.strptime(data['end_date'], '%d/%m/%Y')
        end_date = end_date.replace(tzinfo=tz)

        any_classes = False

        for d in self.daterange(start_date, end_date):
            if d.strftime("%A") == data['day']:
                any_classes = True
                break

        if not any_classes:
            return Response({"No Classes given in start and end date"}, status=200)

        keywords = data.getlist('keywords')

        model_keywords = ""

        for item in keywords:
            model_keywords += item + ","
        model_keywords = model_keywords[:-1]

        gymclass = GymClass.objects.create(
            studio=studio,
            name=data['name'],
            coach=coach,
            enrollment_capacity=data['enrollment_capacity'],
            keywords=model_keywords,
            description=data['description'],
            start_datetime=start_date,
            end_datetime=end_date,
            day=data['day'],
            start_time=start_time,
            end_time=end_time,
        )

        gymclass.save()

        for d in self.daterange(start_date, end_date):
            if d.strftime("%A") == data['day']:
                gymschedule = GymClassSchedule.objects.create(date=d,
                                                              parent_class=gymclass)
                gymschedule.save()

        return Response({"success": True})

    def ValidateData(self, data) -> dict:
        errors = {}
        for key in KEYS:
            if key not in data:
                errors[key] = "Missing Key"

        if 'day' not in errors:
            if data['day'] not in ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                                   'Friday', 'Saturday', 'Sunday']:
                errors['day'] = "Wrong day name. Must be Monday, Tuesday, Wednesday," \
                                " Thursday, Friday, Saturday or Sunday"

        if 'enrollment_capacity' not in errors:
            try:
                int(data['enrollment_capacity'])
            except ValueError:
                errors['enrollment_capacity'] = "Wrong input format integer expected"

        if 'start_date' not in errors:
            try:
                datetime.strptime(data['start_date'], '%d/%m/%Y')
            except ValueError:
                errors['start_date'] = "Wrong Start Date Format"

        if 'start_date' not in errors:
            start = datetime.strptime(data['start_date'], '%d/%m/%Y')
            present = datetime.now()
            if start <= present:
                errors['start_date'] = "Start date must be later than the current date"

        if 'end_date' not in errors:
            try:
                datetime.strptime(data['end_date'], '%d/%m/%Y').date()
            except ValueError:
                errors['end_date'] = "Wrong End Date Format"

        if 'end_date' not in errors:
            start = datetime.strptime(data['start_date'], '%d/%m/%Y')
            end = datetime.strptime(data['end_date'], '%d/%m/%Y')
            if start >= end:
                errors['end_date'] = "End date must be later than the Start date"

        if 'start_time' not in errors:
            try:
                dt.datetime.strptime(data['start_time'], '%H:%M').time()
            except ValueError:
                errors['start_time'] = "Wrong Start Time Format"

        if 'end_time' not in errors:
            try:
                dt.datetime.strptime(data['end_time'], '%H:%M').time()
            except ValueError:
                errors['end_time'] = "Wrong End Time Format"

        if 'end_time' not in errors:
            start_time = dt.datetime.strptime(data['start_time'], '%H:%M').time()
            end_time = dt.datetime.strptime(data['end_time'], '%H:%M').time()

            if start_time >= end_time:
                errors['end_time'] = "End Time must be later than the Start Time"

        return errors

    def daterange(self, date1, date2):
        for n in range(int((date2 - date1).days) + 1):
            yield date1 + timedelta(n)
