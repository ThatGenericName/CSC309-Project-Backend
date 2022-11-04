from django.db import models
from django.contrib.auth.models import User

from studios.models import Studio

# Create your models here.

class GymClass(models.Model):
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE)
    name = models.CharField(null=False, max_length=255)
    description = models.TextField()
    last_modified = models.DateTimeField(auto_now=True)
    keywords = models.TextField()
    capacity = models.IntegerField()
    weekly_schedule = models.ManyToManyField("GymClassSchedule")

class GymClassSchedule(models.Model):
    coach = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.CharField(null=False, max_length=9)
    start_time = models.TimeField(null=False, auto_now=False, auto_now_add=False)
    end_time = models.TimeField(null=False, auto_now=False, auto_now_add=False)

class GymClassOccurence(models.Model):
    coach = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    parent_class = models.ForeignKey(GymClass, on_delete=models.CASCADE)
    start_datetime = models.DateTimeField(null=False, auto_now=False, auto_now_add=False)
    end_datetime = models.DateTimeField(null=False, auto_now=False, auto_now_add=False)
    enrollment_capacity = models.IntegerField()
    enrollment_count = models.IntegerField()


