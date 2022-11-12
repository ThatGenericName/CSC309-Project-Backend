from datetime import timedelta

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from studios.models import Studio

# Create your models here.

dur = timedelta(days=30)

class GymClass(models.Model):
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE)
    coach = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    enrollment_capacity = models.IntegerField(default=10)
    enrollment_count = models.IntegerField(default=0)
    name = models.CharField(null=False, max_length=255)
    description = models.TextField(null=True)
    keywords = models.TextField(null=True)
    start_datetime = models.DateTimeField(null=False, auto_now=False, auto_now_add=False, default=timezone.now)
    end_datetime = models.DateTimeField(null=False, auto_now=False, auto_now_add=False, default=timezone.now() + dur)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        day = self.start_datetime.day
        month = self.start_datetime.month
        return f"{self.name} at {self.studio}, {day}-{month}"

class GymClassSchedule(models.Model):
    date = models.CharField(null=False, max_length=9)
    start_time = models.TimeField(null=False, auto_now=False, auto_now_add=False)
    end_time = models.TimeField(null=False, auto_now=False, auto_now_add=False)
    parent_class = models.ForeignKey(GymClass, on_delete=models.CASCADE)


