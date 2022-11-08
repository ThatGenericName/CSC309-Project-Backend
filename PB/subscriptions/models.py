from django.db import models
from rest_framework import serializers


# Create your models here.

class Subscription(models.Model):
    name = models.CharField(null=False, max_length=100)
    description = models.TextField(null=False)
    price = models.DecimalField(null=False, decimal_places=2, max_digits=10)
    duration = models.DurationField(null=False)
    tgen = models.BooleanField(null=False, default=False)
    available = models.BooleanField(null=False, default=True)

    def __str__(self):
        return self.name

'''
Serializers
'''
class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = [
            'id',
            'name',
            'description',
            'price',
            'duration'
        ]
