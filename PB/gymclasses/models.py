from datetime import timedelta, datetime
import datetime

from django.db import models
from django.utils import timezone
from rest_framework import serializers
from rest_framework.authtoken.admin import User

from studios.models import Studio, StudioSerializer

# Create your models here.


dur = timedelta(days=30)

class GymClass(models.Model):
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE)
    name = models.CharField(null=False, max_length=255)
    description = models.TextField(null=True)
    keywords = models.TextField(null=True)
    earliest_date = models.DateField(null=False, auto_now=False, auto_now_add=False,
                                     default=timezone.now)
    last_date = models.DateField(null=False, auto_now=False, auto_now_add=False,
                                 default=timezone.now() + dur)
    day = models.CharField(null=False, max_length=255, default="Monday")
    start_time = models.TimeField(null=False, auto_now=False, auto_now_add=False,
                                  default=datetime.time(9, 00, 00))
    end_time = models.TimeField(null=False, auto_now=False, auto_now_add=False,
                                default=datetime.time(10, 00, 00))
    last_modified = models.DateTimeField(auto_now=True)

class GymClassSchedule(models.Model):
    date = models.DateField(null=False, auto_now=False, auto_now_add=False,
                            default=timezone.now)
    parent_class = models.ForeignKey(GymClass, on_delete=models.CASCADE, default="")
    coach = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    enrollment_capacity = models.IntegerField(default=10)
    enrollment_count = models.IntegerField(default=0)
    start_time = models.DateTimeField(null=False, auto_now=False, auto_now_add=False,
                                      default=timezone.now)
    end_time = models.DateTimeField(null=False, auto_now=False, auto_now_add=False,
                                    default=timezone.now)


"""

Serializer
"""
class CoachSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'email'
        ]


class GymClassSerializer(serializers.ModelSerializer):
    studio = StudioSerializer
    coach = CoachSerializer

    class Meta:
        model = GymClass
        fields = [
            'studio',
            'name',
            'coach',
            'enrollment_capacity',
            'enrollment_count',
            'description',
            'keywords',
            'start_datetime',
            'end_datetime',
            'day',
            'start_time',
            'end_time',
            'last_modified'
        ]


class GymClassScheduleSerializer(serializers.ModelSerializer):
    parent_class = GymClassSerializer

    class Meta:
        model = GymClassSchedule
        fields = [
            'date',
            'parent_class',
        ]
