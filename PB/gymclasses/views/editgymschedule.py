import json
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


class EditGymClassSchedule(APIView):
    parser_classes = [
        rest_framework.parsers.JSONParser,
        rest_framework.parsers.FormParser,
        rest_framework.parsers.MultiPartParser
    ]

    permission_classes = [IsAdminUser]

    keys = [
        'date',
        'coach',
        'enrollment_capacity',
        'enrollment_count',
        'start_time',
        'end_time',
        'is_cancelled'
    ]

    def post(self, request: Request, *args, **kwargs):

        data = request.data
        gym_class_schedule_id = kwargs["gymclass_schedule_id"]

        errors = self.ValidateData(request.data)

        if len(errors):
            return Response(errors, status=400)

        if not GymClassSchedule.objects.filter(id=gym_class_schedule_id):
            return Response({"Wrong GymClass Id"}, status=404)

        if data["coach"]:
            try:
                User.objects.get(id=data["coach"])
            except ObjectDoesNotExist:
                return Response({'error': 'Coach was not found'}, status=404)

        gym_class_schedule = GymClassSchedule.objects.get(id=gym_class_schedule_id)

        date = gym_class_schedule.date
        coach = gym_class_schedule.coach
        enrollment_capacity = gym_class_schedule.enrollment_capacity
        enrollment_count = gym_class_schedule.enrollment_count
        start_time = gym_class_schedule.start_time
        end_time = gym_class_schedule.end_time
        is_cancelled = gym_class_schedule.is_cancelled

        if data["date"]:
            d = datetime.datetime.strptime(data['date'], '%d/%m/%Y')
            date = datetime.datetime(year=d.year,
                                     month=d.month,
                                     day=d.day).date()
        if data["coach"]:
            coach = User.objects.get(id=data["coach"])
        if data["enrollment_capacity"]:
            enrollment_capacity = data["enrollment_capacity"]
        if data["enrollment_count"]:
            enrollment_count = data["enrollment_count"]
        if data["start_time"]:
            start_time = datetime.datetime.strptime(data['start_time'], '%H:%M').time()
        if data["end_time"]:
            end_time = datetime.datetime.strptime(data['end_time'], '%H:%M').time()
        if data["is_cancelled"]:
            is_cancelled = data["is_cancelled"]

            if start_time >= end_time:
                return Response({"Last date must be later than the Start date"}, status=400)

        if gym_class_schedule.parent_class.earliest_date.year > date.year or \
                gym_class_schedule.parent_class.earliest_date.month > date.month or \
                gym_class_schedule.parent_class.earliest_date.day > date.day or \
                gym_class_schedule.parent_class.last_date.year < date.year or \
                gym_class_schedule.parent_class.last_date.month < date.month or \
                gym_class_schedule.parent_class.last_date.day < date.day:
            return Response({"Date not between class earliest date and last date"}, status=400)

        s = gym_class_schedule.start_time
        s = s.replace(year=date.year)
        s = s.replace(month=date.month)
        s = s.replace(day=date.day)
        s = s.replace(minute=start_time.minute)
        s = s.replace(hour=start_time.hour)

        e = gym_class_schedule.end_time
        e = e.replace(year=date.year)
        e = e.replace(month=date.month)
        e = e.replace(day=date.day)
        e = e.replace(minute=end_time.minute)
        e = e.replace(hour=end_time.hour)

        setattr(gym_class_schedule, "date", date)
        setattr(gym_class_schedule, "coach", coach)
        setattr(gym_class_schedule, "enrollment_capacity", enrollment_capacity)
        setattr(gym_class_schedule, "enrollment_count", enrollment_count)
        setattr(gym_class_schedule, "start_time", s)
        setattr(gym_class_schedule, "end_time", e)
        setattr(gym_class_schedule, "is_cancelled", is_cancelled)

        gym_class_schedule.save()

        return Response({"success": True}, status=200)

    def ValidateData(self, data) -> dict:
        errors = {}
        for key in self.keys:
            if key not in data:
                errors[key] = "Missing Key"

        if 'date' not in errors:
            try:
                datetime.datetime.strptime(data['date'], '%d/%m/%Y')
            except ValueError:
                errors['date'] = "Wrong  Date Format"

        if 'enrollment_capacity' not in errors and data["enrollment_capacity"]:
            try:
                int(data['enrollment_capacity'])
            except ValueError:
                errors['enrollment_capacity'] = "Wrong input format integer expected"

        if 'enrollment_count' not in errors and data["enrollment_count"]:
            try:
                int(data['enrollment_count'])
            except ValueError:
                errors['enrollment_count'] = "Wrong input format integer expected"

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

        if 'is_cancelled' not in errors and data["is_cancelled"]:
            try:
                json.loads(data["is_cancelled"].lower())
            except json.decoder.JSONDecodeError:
                errors['is_cancelled'] = "Wrong input format Boolean expected"

        return errors
