import os

import pytz
from geopy.geocoders import Nominatim
import datetime

import rest_framework.parsers
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from ..models import *

from PB.utility import ValidatePhoneNumber, ValidatePostalCode, ValidatePicture

from studios.models import Studio


class EditGymClass(APIView):
    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    permission_classes = [IsAdminUser]

    keys = [
        'studio',
        'name',
        'description',
        'keywords',
        'earliest_date',
        'last_date',
        'day',
        'start_time',
        'end_time'
    ]

    def post(self, request: Request, *args, **kwargs):

        data = request.data
        gym_class_id = kwargs["gymclass_id"]

        errors = self.ValidateData(request.data)

        if len(errors):
            return Response(errors)

        if not GymClass.objects.filter(id=gym_class_id):
            return Response({"Wrong GymClass Id"})

        if data["studio"] and not Studio.objects.filter(id=data["studio"]):
            return Response({"Wrong Studio Id"})

        gym_class = GymClass.objects.get(id=gym_class_id)

        earliest_date, last_date = gym_class.earliest_date, gym_class.last_date
        start_time, end_time = gym_class.start_time, gym_class.end_time
        day = gym_class.day

        if data["earliest_date"]:
            earliest_date = datetime.datetime.strptime(data['earliest_date'], '%d/%m/%Y')
            earliest_date = earliest_date.replace(tzinfo=pytz.UTC)
        if data["last_date"]:
            last_date = datetime.datetime.strptime(data['last_date'], '%d/%m/%Y')
            last_date = last_date.replace(tzinfo=pytz.UTC)
        if data["start_time"]:
            start_time = datetime.datetime.strptime(data['start_time'], '%H:%M').time()
        if data["end_time"]:
            end_time = datetime.datetime.strptime(data['end_time'], '%H:%M').time()

        if data["day"]:
            day = data["day"]

        if earliest_date >= last_date:
            return Response({"Last date must be later than the Start date"})
        if start_time >= end_time:
            return Response({"Last date must be later than the Start date"})

        if data["studio"]:
            setattr(gym_class, "studio", Studio.objects.get(id=data["studio"]))
        if data["name"]:
            setattr(gym_class, "name", data["name"])
        if data["description"]:
            setattr(gym_class, "description", data["description"])
        if data["keywords"]:
            keywords = data.getlist('keywords')

            model_keywords = ""

            for item in keywords:
                model_keywords += item + ","
            model_keywords = model_keywords[:-1]
            setattr(gym_class, "keywords", model_keywords)

        setattr(gym_class, "earliest_date", earliest_date)
        setattr(gym_class, "last_date", last_date)
        setattr(gym_class, "day", day)
        setattr(gym_class, "start_time", start_time)
        setattr(gym_class, "end_time", end_time)

        gym_class.save()

        GymClassSchedule.objects.filter(parent_class_id=gym_class,
                                        start_time__gt=timezone.now()).delete()

        for d in self.daterange(earliest_date, last_date):
            if d.strftime("%A") == day:
                s = datetime.datetime(year=d.year, month=d.month, day=d.day,
                                      hour=start_time.hour, minute=start_time.minute)
                s = s.replace(tzinfo=pytz.UTC)
                s = s.replace(year=d.year)
                s = s.replace(month=d.month)
                s = s.replace(day=d.day)
                s = s.replace(minute=start_time.minute)
                s = s.replace(hour=start_time.hour)

                e = datetime.datetime(year=d.year, month=d.month, day=d.day,
                                      hour=end_time.hour, minute=end_time.minute)

                e = e.replace(tzinfo=pytz.UTC)
                e = e.replace(year=d.year)
                e = e.replace(month=d.month)
                e = e.replace(day=d.day)
                e = e.replace(minute=end_time.minute)
                e = e.replace(hour=end_time.hour)
                gymschedule = GymClassSchedule.objects.create(date=d,
                                                              coach=User.objects.get(id=1),
                                                              parent_class=gym_class,
                                                              start_time=s,
                                                              end_time=e)

                gymschedule.save()

        gym_class.save()

        return Response({"success": True}, status=200)

    def ValidateData(self, data) -> dict:
        errors = {}
        for key in self.keys:
            if key not in data:
                errors[key] = "Missing Key"

        if 'day' not in errors and data["day"]:
            if data['day'] not in ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                                   'Friday', 'Saturday', 'Sunday']:
                errors['day'] = "Wrong day name. Must be Monday, Tuesday, Wednesday," \
                                " Thursday, Friday, Saturday or Sunday"

        if 'enrollment_capacity' not in errors and data["enrollment_capacity"]:
            try:
                int(data['enrollment_capacity'])
            except ValueError:
                errors['enrollment_capacity'] = "Wrong input format integer expected"

        if 'earliest_date' not in errors and data["earliest_date"]:
            try:
                datetime.datetime.strptime(data['earliest_date'], '%d/%m/%Y')
            except ValueError:
                errors['earliest_date'] = "Wrong Start Date Format"

        if 'earliest_date' not in errors and data["earliest_date"]:
            start = datetime.datetime.strptime(data['earliest_date'], '%d/%m/%Y')
            tz = pytz.timezone('America/Toronto')
            start = start.replace(tzinfo=tz)
            present = timezone.now()
            if start <= present:
                errors['earliest_date'] = "Earliest date must be later than the current date"

        if 'last_date' not in errors and data["last_date"]:
            try:
                datetime.datetime.strptime(data['last_date'], '%d/%m/%Y').date()
            except ValueError:
                errors['last_date'] = "Wrong End Date Format"

        if 'start_time' not in errors and data["start_time"]:
            try:
                datetime.datetime.strptime(data['start_time'], '%H:%M').time()
            except ValueError:
                errors['start_time'] = "Wrong Start Time Format"

        if 'end_time' not in errors and data["end_time"]:
            try:
                datetime.datetime.strptime(data['end_time'], '%H:%M').time()
            except ValueError:
                errors['end_time'] = "Wrong End Time Format"

        return errors

    def daterange(self, date1, date2):
        for n in range(int((date2 - date1).days) + 1):
            yield date1 + timedelta(n)
