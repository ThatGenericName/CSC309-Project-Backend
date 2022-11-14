from datetime import timedelta, datetime
import datetime

from django.utils import timezone
from rest_framework import serializers

# Create your models here.
from PB.studios.models import *
from PB.accounts.models import *

dur = timedelta(days=30)


class GymClass(models.Model):
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE)
    name = models.CharField(null=False, max_length=255)
    coach = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    enrollment_capacity = models.IntegerField(default=10)
    enrollment_count = models.IntegerField(default=0)
    description = models.TextField(null=True)
    keywords = models.TextField(null=True)
    start_datetime = models.DateField(null=False, auto_now=False, auto_now_add=False,
                                      default=timezone.now)
    end_datetime = models.DateField(null=False, auto_now=False, auto_now_add=False,
                                    default=timezone.now() + dur)
    day = models.CharField(null=False, max_length=255, default="Monday")
    start_time = models.TimeField(null=False, auto_now=False, auto_now_add=False,
                                  default=datetime.time(9, 00, 00))
    end_time = models.TimeField(null=False, auto_now=False, auto_now_add=False,
                                default=datetime.time(10, 00, 00))
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        day = self.start_datetime.day
        month = self.start_datetime.month
        return f"{self.name} at {self.studio}, {day}-{month}"


class GymClassSchedule(models.Model):
    date = models.DateField(null=False, auto_now=False, auto_now_add=False,
                            default=timezone.now)
    parent_class = models.ForeignKey(GymClass, on_delete=models.CASCADE, default="")


"""
Serializer
"""


class GymClassSerializer(serializers.ModelSerializer):
    studio = StudioSerializer
    coach = UserExtendedSerializer

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
