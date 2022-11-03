from django.db import models

# Create your models here.

class Subscription(models.Model):
    name = models.CharField(null=False, max_length=100)
    description = models.TextField(null=False)
    price = models.DecimalField(null=False, decimal_places=2, max_digits=10)
    duration = models.DurationField(null=False)


