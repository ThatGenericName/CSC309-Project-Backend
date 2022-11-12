from django.db import models
from django.contrib.auth.models import User

from studios.models import Studio

# Create your models here.

class GymClass(models.Model):
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE)
    coach = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    enrollment_capacity = models.IntegerField()
    enrollment_count = models.IntegerField()
    name = models.CharField(null=False, max_length=255)
    description = models.TextField()
    keywords = models.TextField()
    start_datetime = models.DateTimeField(null=False, auto_now=False, auto_now_add=False)
    end_datetime = models.DateTimeField(null=False, auto_now=False, auto_now_add=False)
    last_modified = models.DateTimeField(auto_now=True)

class GymClassSchedule(models.Model):
    date = models.CharField(null=False, max_length=9)
    start_time = models.TimeField(null=False, auto_now=False, auto_now_add=False)
    end_time = models.TimeField(null=False, auto_now=False, auto_now_add=False)
    parent_class = models.ForeignKey(GymClass, on_delete=models.CASCADE)


