import datetime as dt
from datetime import datetime, timedelta
from pytz import timezone
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
DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']


class ClassesofStudio(APIView):
    '''
    edits a specific profile
    '''

    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    # permission_classes = [IsAuthenticated]

    def get(self, request: Request, *args, **kwargs):

        studio_id = kwargs['studio_id']
        tz = timezone('EST')

        try:
            studio = Studio.objects.get(id=studio_id)
        except ObjectDoesNotExist:
            return Response({'error': 'Studio Class was not found'}, status=404)

        classes = GymClass.objects.filter(studio_id=studio)
        day_now = datetime.now().strftime("%A")

        list_of_days = DAYS[DAYS.index(day_now):] + \
                       DAYS[:DAYS.index(day_now)]

        lst = []
        time_now = datetime.now(tz).time()

        for item in list_of_days:
            class_for_day = classes.filter(day=item).\
                order_by('start_time')

            for gym_class in class_for_day:
                if item == day_now and gym_class.start_time < time_now:
                    continue
                lst.append({
                    "name": gym_class.name,
                    "coach": gym_class.coach.username,
                    "enrollment_capacity": gym_class.enrollment_capacity,
                    "enrollment_count": gym_class.enrollment_count,
                    "description": gym_class.description,
                    "keywords": gym_class.keywords,
                    "Start Date": gym_class.start_datetime.strftime("%m/%d/%Y"),
                    "End Date": gym_class.end_datetime.strftime("%m/%d/%Y"),
                    "day": gym_class.day,
                    "Start Time": gym_class.start_time.strftime("%H:%M"),
                    "End Time": gym_class.end_time.strftime("%H:%M"),
                })

        class_for_day = classes.filter(day=day_now).order_by('start_time')

        for gym_class in class_for_day:
            if gym_class.start_time < time_now:
                lst.append({
                    "name": gym_class.name,
                    "coach": gym_class.coach.username,
                    "enrollment_capacity": gym_class.enrollment_capacity,
                    "enrollment_count": gym_class.enrollment_count,
                    "description": gym_class.description,
                    "keywords": gym_class.keywords,
                    "Start Date": gym_class.start_datetime.strftime("%m/%d/%Y"),
                    "End Date": gym_class.end_datetime.strftime("%m/%d/%Y"),
                    "day": gym_class.day,
                    "Start Time": gym_class.start_time.strftime("%H:%M"),
                    "End Time": gym_class.end_time.strftime("%H:%M"),
                })

        return Response(lst)
